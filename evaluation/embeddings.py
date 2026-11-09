"""Gemini sentence-similarity embeddings with run-local caching and usage."""

import os
from contextvars import ContextVar
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Protocol, Sequence

import numpy as np
from google import genai
from google.genai import types
from numpy.typing import NDArray

from model_runtime import sum_usage
from schemas import UsageRecord

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_INSTRUCTION = "task: sentence similarity | query: "
_MAX_BATCH_SIZE = 100

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


def _reported_count(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def _capture_usage(response: Any) -> None:
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


class GeminiEmbedder:
    """Reuse one instance across the experiment to share cached vectors."""

    def __init__(
        self, *, model_version: str = EMBEDDING_MODEL, client_args: dict[str, Any] | None = None
    ) -> None:
        # The service currently exposes a model alias. Keep the version in the
        # cache namespace separately so a deployment can identify its revision.
        self._model_version = model_version
        self._client_args = dict(client_args or {})
        self._client: genai.Client | None = None
        self._cache: dict[_ModelKey, _Vector] = {}
        self._lock = Lock()

    def close(self) -> None:
        """Close the transport once the experiment is done."""
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            api_key = os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
            if not api_key:
                raise EmbeddingError(
                    "Set GOOGLE_API_KEY or GEMINI_API_KEY to use Gemini embeddings",
                    usage=UsageRecord(input_tokens=0, output_tokens=0),
                    request_count=0,
                )
            client_args = dict(self._client_args)
            hooks = dict(client_args.get("event_hooks", {}))
            hooks["response"] = [*hooks.get("response", ()), _capture_usage]
            client_args["event_hooks"] = hooks
            self._client = genai.Client(
                vertexai=False,
                api_key=api_key,
                http_options=types.HttpOptions(
                    api_version="v1beta",
                    client_args=client_args,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
        return self._client

    def embed(self, texts: list[str]) -> EmbeddingBatch:
        keys = [
            (EMBEDDING_MODEL, self._model_version, EMBEDDING_INSTRUCTION, text)
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
        for start in range(0, len(missing), _MAX_BATCH_SIZE):
            batch = missing[start : start + _MAX_BATCH_SIZE]
            contents = [
                types.Content(parts=[types.Part.from_text(text=instruction + text)])
                for _, _, instruction, text in batch
            ]
            captured: list[UsageRecord] = []
            token = _CAPTURED_USAGE.set(captured)
            request_count += 1
            failure = None
            try:
                response = client.models.embed_content(model=EMBEDDING_MODEL, contents=contents)
            except Exception as error:
                failure = f"Gemini embedding request failed ({type(error).__name__})"
            finally:
                _CAPTURED_USAGE.reset(token)
            usage_records.append(sum_usage(captured))
            if failure is not None:
                raise EmbeddingError(
                    failure, usage=sum_usage(usage_records), request_count=request_count
                ) from None
            embeddings = response.embeddings or []
            vectors = vector_matrix(
                EmbeddingBatch(
                    [embedding.values or [] for embedding in embeddings],
                    sum_usage(usage_records),
                    request_count,
                ),
                len(batch),
            )
            pending.update((key, tuple(vector.tolist())) for key, vector in zip(batch, vectors, strict=True))

        result = EmbeddingBatch(
            [pending[key] if key in pending else self._cache[key] for key in keys],
            sum_usage(usage_records),
            request_count,
        )
        vector_matrix(result, len(keys))
        self._cache.update(pending)
        return result
