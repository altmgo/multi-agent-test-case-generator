"""Structured Gemini calls with complete requirements and auditable token usage."""

import json
import os
from contextvars import ContextVar
from dataclasses import replace
from typing import Any, Literal, Protocol, TypeVar

from google.genai.types import (
    ContentUnionDict,
    FinishReason,
    GenerateContentConfigDict,
    GenerateContentResponse,
    HttpRetryOptions,
    Modality,
)
from pydantic import BaseModel, TypeAdapter, computed_field
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.exceptions import (
    ModelAPIError,
    ModelConnectionError,
    ModelHTTPError,
    UnexpectedModelBehavior,
)
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
)
from pydantic_ai.models import Model, ModelRequestParameters
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.models.wrapper import WrapperModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.settings import ModelSettings

from schemas import GenerationInput, UsageRecord

T = TypeVar("T")

GENERATION_MODELS = frozenset({"gemini-3.5-flash-lite", "gemini-3.8-flash"})
DEFAULT_CONTEXT_LIMIT = 1_048_576
DEFAULT_OUTPUT_TOKENS = 8192
_MAX_OUTPUT_TOKENS = 65_536
_REQUEST_OVERHEAD_TOKENS = 32
_MODE_INSTRUCTIONS = {
    "batch": "Return the requested cases together in a single output.",
    "per_requirement": "Return cases only for the requirement targeted by this stage.",
    "per_case": "Return only the single case targeted by this stage.",
}


class Runtime(Protocol):
    """Generation boundary shared by Gemini and test doubles.

    Each run may append multiple provider attempts to usage_records. Extras must
    be JSON-compatible stage data. Only extra["history"] may be dropped to fit.
    Case generation stages can set extra["output_mode"] to batch,
    per_requirement, or per_case. The stage supplies the target if applicable.
    """

    usage_records: list[UsageRecord]

    async def run(
        self,
        stage: str,
        instructions: str,
        input: GenerationInput,
        output_type: type[T],
        *,
        extra: dict[str, Any] | None = None,
    ) -> T: ...


class ContextLimitError(ValueError):
    """The estimated request and reserved output exceed the context budget."""


def check_context(input_tokens: int, output_tokens: int, limit: int) -> None:
    """Require the estimated input and reserved output to fit together."""
    if input_tokens < 0 or output_tokens < 0 or limit <= 0:
        raise ValueError("Token counts must be nonnegative and the context limit positive")
    if input_tokens + output_tokens > limit:
        raise ContextLimitError(
            f"Estimated context of {input_tokens} input and {output_tokens} output tokens exceeds {limit}"
        )


def _complete_total(values: list[int | None]) -> int | None:
    if not values or None in values:
        return None
    return sum(value for value in values if value is not None)


def sum_usage(records: list[UsageRecord]) -> UsageRecord:
    """Sum only counters reported by every attempt in the group."""
    details = [record.details or {} for record in records]
    common_keys = set(details[0]).intersection(*details[1:]) if details else set()
    return UsageRecord(
        input_tokens=_complete_total([record.input_tokens for record in records]),
        output_tokens=_complete_total([record.output_tokens for record in records]),
        details={key: sum(detail[key] for detail in details) for key in sorted(common_keys)} or None,
    )


# Pydantic AI normalizes omitted Gemini counters to zero. The scoped value
# keeps the SDK's raw availability even if Pydantic AI cannot process the reply.
_RAW_USAGE: ContextVar[list[UsageRecord] | None] = ContextVar("gemini_usage", default=None)


_USAGE_DETAIL_COUNTERS = (
    ("cached_content_tokens", "cachedContentTokenCount"),
    ("thoughts_tokens", "thoughtsTokenCount"),
    ("tool_use_prompt_tokens", "toolUsePromptTokenCount"),
    ("total_tokens", "totalTokenCount"),
)
_USAGE_MODALITY_BREAKDOWNS = (
    ("prompt", "promptTokensDetails"),
    ("cache", "cacheTokensDetails"),
    ("candidates", "candidatesTokensDetails"),
    ("tool_use_prompt", "toolUsePromptTokensDetails"),
)
_MODALITY_NAMES = {modality.value: modality.value.lower() for modality in Modality}


def _reported_count(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def _capture_usage(metadata: object) -> None:
    capture = _RAW_USAGE.get()
    if capture is None or not isinstance(metadata, dict):
        return

    details = {}
    for key, field in _USAGE_DETAIL_COUNTERS:
        count = _reported_count(metadata.get(field))
        if count is not None:
            details[key] = count
    for prefix, field in _USAGE_MODALITY_BREAKDOWNS:
        entries = metadata.get(field)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            raw_modality = entry.get("modality")
            modality = _MODALITY_NAMES.get(raw_modality.upper()) if isinstance(raw_modality, str) else None
            count = _reported_count(entry.get("tokenCount"))
            if modality is not None and count is not None:
                details[f"{modality}_{prefix}_tokens"] = count

    capture.append(UsageRecord(
        input_tokens=_reported_count(metadata.get("promptTokenCount")),
        output_tokens=_reported_count(metadata.get("candidatesTokenCount")),
        details=details or None,
    ))


def _capture_http_error_usage(body: object) -> None:
    if not isinstance(body, dict):
        return
    metadata = body.get("usageMetadata")
    if not isinstance(metadata, dict) and isinstance(body.get("error"), dict):
        metadata = body["error"].get("usageMetadata")
    # Parse only known counters and modalities without decoding the untrusted
    # body as an SDK model, whose enum parser may warn with raw field values.
    _capture_usage(metadata)


class _GeminiModel(GoogleModel):
    async def _build_content_and_config(
        self,
        messages: list[ModelMessage],
        model_settings: GoogleModelSettings,
        model_request_parameters: ModelRequestParameters,
    ) -> tuple[list[ContentUnionDict], GenerateContentConfigDict]:
        contents, config = await super()._build_content_and_config(
            messages, model_settings, model_request_parameters
        )
        # The SDK otherwise sends continuation requests inside this one model call.
        config["automatic_continuation"] = False
        return contents, config

    def _process_response(
        self, response: GenerateContentResponse, model_request_parameters: ModelRequestParameters
    ) -> ModelResponse:
        metadata = response.usage_metadata
        if _RAW_USAGE.get() is not None and metadata is not None:
            _capture_usage(metadata.model_dump(mode="json", by_alias=True, exclude_none=True))
        return super()._process_response(response, model_request_parameters)

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        safe_error: Exception
        try:
            response = await super().request(messages, model_settings, model_request_parameters)
        except ModelHTTPError as error:
            _capture_http_error_usage(error.body)
            safe_error = type(error)(status_code=error.status_code, model_name=self.model_name)
        except ModelConnectionError as error:
            safe_error = type(error)(self.model_name, "Gemini connection failed", phase=error.phase)
        except ModelAPIError:
            safe_error = ModelAPIError(self.model_name, "Gemini API request failed")
        except Exception as error:
            safe_error = UnexpectedModelBehavior(f"Gemini request failed ({type(error).__name__})")
        else:
            if (response.provider_details or {}).get("finish_reason") == FinishReason.CONTINUATION.value:
                raise UnexpectedModelBehavior("Gemini returned an unsupported continuation response")
            return response

        # Raising outside the handlers keeps the provider error and its request
        # or response objects out of both the explicit and implicit chains.
        raise safe_error from None


def make_model(model_id: str) -> Model:
    """Create an allowlisted Gemini Developer API model from an environment key."""
    if model_id not in GENERATION_MODELS:
        raise ValueError("Unsupported generation model")
    api_key = os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Set GOOGLE_API_KEY or GEMINI_API_KEY to use Gemini")
    provider = GoogleProvider(api_key=api_key, retry_options=HttpRetryOptions(attempts=1))
    return _GeminiModel(model_id, provider=provider)


class ContextEstimate(BaseModel):
    """Local preflight estimate, separate from Gemini's reported token usage."""

    requirements_tokens: int
    instructions_tokens: int
    extra_tokens: int
    history_tokens: int = 0
    schema_tokens: int
    output_tokens: int
    framing_tokens: int = _REQUEST_OVERHEAD_TOKENS

    @computed_field
    @property
    def input_tokens(self) -> int:
        return (
            self.requirements_tokens
            + self.instructions_tokens
            + self.extra_tokens
            + self.history_tokens
            + self.schema_tokens
            + self.framing_tokens
        )


class CallRecord(BaseModel):
    """One provider attempt or a request refused by the local context check."""

    stage: str
    unit_id: str
    model_id: str
    call_id: int
    attempt: int
    context: ContextEstimate
    history_dropped: bool = False
    status: Literal["responded", "succeeded", "retry", "failed", "context_exceeded"] = "responded"
    usage: UsageRecord
    error_type: str | None = None


def _json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, allow_nan=False)


def _estimate_tokens(data: str | bytes) -> int:
    size = len(data.encode("utf-8")) if isinstance(data, str) else len(data)
    return (size + 2) // 3


def _reject_reference_cases(data: Any) -> None:
    if isinstance(data, dict):
        if "reference_cases" in data or {"link_method", "link_status"} <= data.keys():
            raise ValueError("Reference cases cannot be included in generation extras")
        for value in data.values():
            _reject_reference_cases(value)
    elif isinstance(data, (list, tuple)):
        for value in data:
            _reject_reference_cases(value)


class _AuditedModel(WrapperModel):
    def __init__(
        self,
        runtime: "ModelRuntime",
        stage: str,
        unit_id: str,
        call_id: int,
        estimate: ContextEstimate,
        prompt_without_history: str,
        optional_history_tokens: int,
    ):
        super().__init__(runtime._model)
        self.runtime = runtime
        self.stage = stage
        self.unit_id = unit_id
        self.call_id = call_id
        self.estimate = estimate
        self.prompt_without_history = prompt_without_history
        self.optional_history_tokens = optional_history_tokens
        self.history_dropped = False
        self.records: list[CallRecord] = []

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        if self.records and self.records[-1].status == "responded":
            self.records[-1].status = "retry"

        # The fresh Agent starts with our full prompt. Subsequent messages are
        # response and validation feedback added by Pydantic AI for a retry.
        retry_history_tokens = (
            _estimate_tokens(ModelMessagesTypeAdapter.dump_json(messages[1:], exclude_defaults=True))
            if len(messages) > 1
            else 0
        )
        first = messages[0]
        if not isinstance(first, ModelRequest):
            raise RuntimeError("Expected the initial generation prompt")
        estimate = self.estimate.model_copy(update={
            "history_tokens": retry_history_tokens,
            "instructions_tokens": self.estimate.instructions_tokens + sum(
                _estimate_tokens(part.content) for part in first.parts if isinstance(part, SystemPromptPart)
            ),
        })
        if self.optional_history_tokens and not self.history_dropped:
            if estimate.input_tokens + self.optional_history_tokens + estimate.output_tokens <= self.runtime.context_limit:
                estimate.history_tokens += self.optional_history_tokens
            else:
                self.history_dropped = True

        record = CallRecord(
            stage=self.stage,
            unit_id=self.unit_id,
            model_id=self.wrapped.model_name,
            call_id=self.call_id,
            attempt=len(self.records) + 1,
            context=estimate,
            history_dropped=self.history_dropped,
            usage=UsageRecord(),
        )
        self.records.append(record)
        self.runtime.call_records.append(record)
        try:
            check_context(estimate.input_tokens, estimate.output_tokens, self.runtime.context_limit)
        except ContextLimitError as error:
            record.status = "context_exceeded"
            record.error_type = type(error).__name__
            raise

        if self.history_dropped:
            new_first = replace(first, parts=[
                replace(part, content=self.prompt_without_history) if isinstance(part, UserPromptPart) else part
                for part in first.parts
            ])
            messages = [new_first, *messages[1:]]

        capture: list[UsageRecord] = []
        token = _RAW_USAGE.set(capture)
        try:
            return await super().request(messages, model_settings, model_request_parameters)
        except BaseException as error:
            record.status = "failed"
            record.error_type = type(error).__name__
            raise
        finally:
            if capture:
                record.usage = capture[-1]
            self.runtime.usage_records.append(record.usage)
            _RAW_USAGE.reset(token)


class ModelRuntime:
    """Run typed stages with an independent Gemini conversation for each stage."""

    def __init__(
        self,
        model_id: str,
        *,
        context_limit: int = DEFAULT_CONTEXT_LIMIT,
        output_tokens: int = DEFAULT_OUTPUT_TOKENS,
        retries: int = 1,
    ):
        if not 0 < context_limit <= DEFAULT_CONTEXT_LIMIT:
            raise ValueError(f"Context limit must be between 1 and {DEFAULT_CONTEXT_LIMIT}")
        if not 0 < output_tokens <= _MAX_OUTPUT_TOKENS:
            raise ValueError(f"Output tokens must be between 1 and {_MAX_OUTPUT_TOKENS}")
        if retries < 0:
            raise ValueError("Retries must be nonnegative")
        self._model = make_model(model_id)
        self.context_limit = context_limit
        self.output_tokens = output_tokens
        self.retries = retries
        self._call_count = 0
        self.call_records: list[CallRecord] = []
        self.usage_records: list[UsageRecord] = []

    async def run(
        self,
        stage: str,
        instructions: str,
        input: GenerationInput,
        output_type: type[T],
        *,
        extra: dict[str, Any] | None = None,
    ) -> T:
        extra = dict(extra or {})
        _reject_reference_cases(extra)
        if "output_mode" in extra:
            mode = extra["output_mode"]
            if not isinstance(mode, str) or mode not in _MODE_INSTRUCTIONS:
                raise ValueError("Unsupported case output mode")
            instructions = f"{instructions}\n{_MODE_INSTRUCTIONS[mode]}"

        payload = {
            "unit_id": input.unit_id,
            "requirements": [
                requirement.model_dump(mode="json", include={"id", "text", "language", "source"})
                for requirement in input.requirements
            ],
        }
        required_extra = {key: value for key, value in extra.items() if key != "history"}
        estimate = ContextEstimate(
            requirements_tokens=_estimate_tokens(_json(payload)),
            instructions_tokens=_estimate_tokens(instructions),
            extra_tokens=_estimate_tokens(_json(required_extra)) if required_extra else 0,
            schema_tokens=_estimate_tokens(_json(TypeAdapter(output_type).json_schema())),
            output_tokens=self.output_tokens,
        )
        prompt_without_history = _json({**payload, "extra": required_extra} if required_extra else payload)
        self._call_count += 1
        model = _AuditedModel(
            self, stage, input.unit_id, self._call_count, estimate, prompt_without_history,
            _estimate_tokens(_json({"history": extra["history"]})) if "history" in extra else 0,
        )
        agent = Agent(
            model,
            instructions=instructions,
            output_type=NativeOutput(output_type),
            retries=self.retries,
            model_settings={"max_tokens": self.output_tokens},
        )
        try:
            result = await agent.run(_json({**payload, "extra": extra} if extra else payload))
        except BaseException as error:
            if not model.records or model.records[-1].status != "responded":
                raise
            model.records[-1].status = "failed"
            model.records[-1].error_type = type(error).__name__
            if not isinstance(error, UnexpectedModelBehavior):
                raise
            safe_error = type(error)("Gemini output was rejected")
        else:
            model.records[-1].status = "succeeded"
            return result.output

        raise safe_error from None
