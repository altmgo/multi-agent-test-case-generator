"""Gemini sentence-similarity embeddings with run-local caching and usage."""

import math
import sys
from collections import deque
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from threading import Lock
from time import monotonic, sleep
from typing import Any, Protocol, Sequence

import numpy as np
import httpx
import httpx2
from google import genai
from google.genai import errors, types
from numpy.typing import NDArray

from src.tcg.runtime import MAX_GENERATION_RETRIES, MAX_RETRY_WAIT_SECONDS, sum_usage
from src.tcg.schemas import UsageRecord

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_MODELS = (EMBEDDING_MODEL, "gemini-embedding-001")
EMBEDDING_INSTRUCTION = "task: sentence similarity | query: "
_MAX_BATCH_SIZE = 20
_TEXTS_PER_MINUTE = 100
_WINDOW_SECONDS = 60
_MIN_REQUEST_INTERVAL = 2

_ModelKey = tuple[str, str, str, str]
_Vector = tuple[float, ...]


def canonical_text(title: str, description: str) -> str:
    """Join semantic case fields and collapse whitespace."""
    return " ".join(f"{title} {description}".split())


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: Sequence[Sequence[float]] | NDArray[np.float64]
    usage: UsageRecord = field(default_factory=UsageRecord)
    request_count: int | None = None


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> EmbeddingBatch:
        """Return one vector per canonical input, in input order."""
        ...


class EmbeddingError(ValueError):
    """Embedding failed, with any known usage for the attempted operation."""

    def __init__(
        self, message: str, *, usage: UsageRecord | None = None, request_count: int | None = None
    ) -> None:
        super().__init__(message)
        self.usage = usage if usage is not None else UsageRecord()
        self.request_count = request_count


class EmbeddingQuotaStop(EmbeddingError):
    """The embedding quota prevents continuing this evaluation."""


def _quota_hint(error: errors.APIError) -> tuple[float, bool]:
    """Extract timing and quota classification without logging provider payloads."""
    headers = getattr(error.response, "headers", {})
    raw = headers.get("Retry-After")
    wait = 0.0
    if raw:
        try:
            wait = float(raw)
        except ValueError:
            try:
                date = parsedate_to_datetime(raw)
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)
                wait = (date - datetime.now(timezone.utc)).total_seconds()
            except (TypeError, ValueError, OverflowError):
                pass
    wait = max(0.0, wait) if math.isfinite(wait) else 0.0
    body = error.details if isinstance(error.details, dict) else {}
    body = body.get("error", body)
    if not isinstance(body, dict):
        return wait, False
    exhausted = body.get("type") in ("quota_exceeded", "insufficient_quota")
    details = body.get("details", [])
    for detail in details if isinstance(details, list) else []:
        if not isinstance(detail, dict):
            continue
        if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
            delay = detail.get("retryDelay")
            if isinstance(delay, str) and delay.endswith("s"):
                try:
                    seconds = float(delay[:-1])
                except ValueError:
                    continue
                if math.isfinite(seconds):
                    wait = max(wait, seconds)
        elif detail.get("@type") == "type.googleapis.com/google.rpc.QuotaFailure":
            violations = detail.get("violations")
            for violation in violations if isinstance(violations, list) else []:
                if isinstance(violation, dict) and any(
                    label in str(violation.get(field, "")).lower()
                    for field in ("quotaId", "quotaMetric") for label in ("perday", "per_day", "daily")
                ):
                    exhausted = True
    return wait, exhausted


def vector_matrix(batch: EmbeddingBatch, count: int) -> NDArray[np.float64]:
    """Validate the provider's shape, cardinality and nonzero finite vectors."""
    try:
        vectors = np.asarray(batch.vectors)
        if vectors.dtype.kind not in "iuf":
            raise ValueError("expected real numbers")
        vectors = vectors.astype(np.float64, copy=False)
    except (TypeError, ValueError, OverflowError):
        vectors = np.empty((0, 0))
    if (
        vectors.ndim != 2
        or vectors.shape[0] != count
        or not vectors.shape[1]
        or not np.isfinite(vectors).all()
        or not np.any(vectors, axis=1).all()
    ):
        raise EmbeddingError(
            f"Expected {count} finite, nonzero embedding vectors of the same dimension",
            usage=batch.usage,
            request_count=batch.request_count,
        )
    return vectors


_CAPTURED_USAGE: ContextVar[list[UsageRecord] | None] = ContextVar("embedding_usage", default=None)


class _InvalidWireEmbedding(ValueError):
    """A successful Gemini response contained an invalid raw vector."""


def _reported_count(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def _capture_response(response: Any) -> None:
    # google-genai 3.0.0 filters out Developer API usageMetadata while decoding
    # embedding responses. Read it from the transport before SDK conversion.
    capture = _CAPTURED_USAGE.get()
    if capture is None:
        return
    response.read()
    try:
        payload = response.json()
    except ValueError:
        return
    if not isinstance(payload, dict):
        return

    usage = payload.get("usageMetadata")
    if not isinstance(usage, dict):
        error = payload.get("error")
        usage = error.get("usageMetadata") if isinstance(error, dict) else None
    usage = usage if isinstance(usage, dict) else {}
    details = {}
    modalities = usage.get("promptTokenDetails")
    if isinstance(modalities, list):
        for item in modalities:
            if isinstance(item, dict) and item.get("modality") == "TEXT":
                count = _reported_count(item.get("tokenCount"))
                if count is not None:
                    details["text_prompt_tokens"] = count
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        count = _reported_count(metadata.get("billableCharacterCount"))
        if count is not None:
            details["billable_characters"] = count
    capture.append(UsageRecord(
        input_tokens=_reported_count(usage.get("promptTokenCount")),
        details=details or None,
    ))
    if not response.is_success:
        return

    # The SDK coerces booleans and numeric strings to floats. Check the JSON
    # coordinates before decoding so invalid values never enter the cache.
    embeddings = payload.get("embeddings")
    if not isinstance(embeddings, list):
        raise _InvalidWireEmbedding
    for embedding in embeddings:
        values = embedding.get("values") if isinstance(embedding, dict) else None
        if not isinstance(values, list) or any(type(value) not in (int, float) for value in values):
            raise _InvalidWireEmbedding


class GeminiEmbedder:
    """Reuse one instance across the experiment to share cached vectors."""

    def __init__(
        self, *, model: str, api_key: str, client_args: dict[str, Any] | None = None
    ) -> None:
        if model not in EMBEDDING_MODELS:
            raise ValueError("Unsupported Gemini embedding model")
        self._model = model
        self._api_key = api_key
        self._instruction = EMBEDDING_INSTRUCTION if model == EMBEDDING_MODEL else ""
        self._client_args = dict(client_args or {})
        self._client: genai.Client | None = None
        self._cache: dict[_ModelKey, _Vector] = {}
        self._lock = Lock()
        self._recent: deque[tuple[float, int]] = deque()
        self._next_request = 0.0

    def close(self) -> None:
        """Close the transport once the experiment is done."""
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            if not self._api_key:
                raise EmbeddingError(
                    "Set GOOGLE_API_KEY in .env to use Gemini embeddings",
                    usage=UsageRecord(input_tokens=0, output_tokens=0),
                    request_count=0,
                )
            client_args = dict(self._client_args)
            hooks = dict(client_args.get("event_hooks", {}))
            hooks["response"] = [*hooks.get("response", ()), _capture_response]
            client_args["event_hooks"] = hooks
            self._client = genai.Client(
                vertexai=False,
                api_key=self._api_key,
                http_options=types.HttpOptions(
                    api_version="v1beta",
                    client_args=client_args,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
        return self._client

    def embed(self, texts: list[str]) -> EmbeddingBatch:
        keys = [
            (self._model, self._model, self._instruction, text)
            for text in texts
        ]
        with self._lock:
            missing = [key for key in dict.fromkeys(keys) if key not in self._cache]
            if not missing:
                return EmbeddingBatch(
                    [self._cache[key] for key in keys],
                    UsageRecord(input_tokens=0, output_tokens=0),
                    request_count=0,
                )
            return self._fetch(keys, missing)

    def _fetch(self, keys: list[_ModelKey], missing: list[_ModelKey]) -> EmbeddingBatch:
        client = self._get_client()
        pending: dict[_ModelKey, _Vector] = {}
        usage_records: list[UsageRecord] = []
        request_count = 0
        config = types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY") if self._model != EMBEDDING_MODEL else None
        for start in range(0, len(missing), _MAX_BATCH_SIZE):
            batch = missing[start : start + _MAX_BATCH_SIZE]
            contents = [
                types.Content(parts=[types.Part.from_text(text=instruction + text)])
                for _, _, instruction, text in batch
            ]
            delay = 0.0
            label = f"Gemini embeddings ({self._model}), batch {start // _MAX_BATCH_SIZE + 1}"
            for attempt in range(1, MAX_GENERATION_RETRIES + 2):
                self._pace(len(batch), label)
                captured: list[UsageRecord] = []
                token = _CAPTURED_USAGE.set(captured)
                request_count += 1
                hint = 0.0
                exhausted = rate_limited = False
                try:
                    response = client.models.embed_content(model=self._model, contents=contents, config=config)
                    vectors = vector_matrix(
                        EmbeddingBatch([embedding.values or [] for embedding in response.embeddings or []]),
                        len(batch),
                    )
                except errors.APIError as error:
                    failure = f"HTTP {error.code}"
                    rate_limited = error.code == 429
                    retryable = rate_limited or error.code in {408, 500, 502, 503, 504}
                    hint, exhausted = _quota_hint(error)
                except (EmbeddingError, _InvalidWireEmbedding):
                    failure = "invalid embedding vectors"
                    retryable = True
                except (httpx.TransportError, httpx2.TransportError) as error:
                    failure = type(error).__name__
                    retryable = True
                except Exception as error:
                    failure = type(error).__name__
                    retryable = False
                else:
                    if attempt > 1:
                        print(f"{label}: succeeded on attempt {attempt}", file=sys.stderr, flush=True)
                    break
                finally:
                    _CAPTURED_USAGE.reset(token)
                    usage_records.append(sum_usage(captured))

                delay = max((15 if rate_limited else 2) * 2 ** (attempt - 1), delay + 1, hint)
                stop = exhausted or (rate_limited and (delay > MAX_RETRY_WAIT_SECONDS or attempt > MAX_GENERATION_RETRIES))
                if stop or not retryable or attempt > MAX_GENERATION_RETRIES or delay > MAX_RETRY_WAIT_SECONDS:
                    reason = f"{label}: attempt {attempt} failed ({failure})"
                    if hint > MAX_RETRY_WAIT_SECONDS:
                        reason += f"; provider requested {hint:g}s"
                    error_type = EmbeddingQuotaStop if stop else EmbeddingError
                    raise error_type(reason, usage=sum_usage(usage_records), request_count=request_count)
                print(f"{label}: attempt {attempt} failed ({failure}); retry {attempt}/{MAX_GENERATION_RETRIES} "
                      f"in at least {delay:g}s", file=sys.stderr, flush=True)
                sleep(delay)
            pending.update((key, tuple(vector.tolist())) for key, vector in zip(batch, vectors, strict=True))

        result = EmbeddingBatch(
            [pending[key] if key in pending else self._cache[key] for key in keys],
            sum_usage(usage_records),
            request_count,
        )
        vector_matrix(result, len(keys))
        self._cache.update(pending)
        return result

    def _pace(self, size: int, label: str) -> None:
        now = monotonic()
        while self._recent and self._recent[0][0] <= now:
            self._recent.popleft()
        remaining = sum(count for _, count in self._recent)
        ready = self._next_request
        for expires, count in self._recent:
            if remaining + size <= _TEXTS_PER_MINUTE:
                break
            remaining -= count
            ready = max(ready, expires)
        if ready > now:
            delay = ready - now
            if delay >= 1:
                print(f"{label}: pacing, waiting {delay:.1f}s", file=sys.stderr, flush=True)
            sleep(delay)
        started = monotonic()
        self._next_request = started + _MIN_REQUEST_INTERVAL
        self._recent.append((started + _WINDOW_SECONDS, size))
