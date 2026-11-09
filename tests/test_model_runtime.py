import asyncio
import json
import traceback

import httpx2
import pytest
from pydantic import BaseModel
from pydantic_ai.exceptions import ModelAuthenticationError, ModelHTTPError, UnexpectedModelBehavior
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

import model_runtime
from model_runtime import (
    ContextLimitError,
    ModelRuntime,
    check_context,
    make_model,
    sum_usage,
)
from schemas import GenerationInput, ReferenceCase, Requirement, UsageRecord


class Answer(BaseModel):
    decision: str


@pytest.fixture
def requirements():
    return GenerationInput(
        unit_id="sample",
        requirements=[
            Requirement(id="R1", text="Keep bookmarks.", language="en", source="fixture"),
            Requirement(id="R2", text="Reabrir após reiniciar.", language="pt", source="fixture"),
        ],
    )


def test_missing_key_reports_only_configuration(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "   ")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GOOGLE_API_KEY") as error:
        make_model("gemini-3.5-flash-lite")

    assert "   " not in str(error.value)


def test_disallowed_model_is_rejected_without_echoing_input(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "secret-shaped-model-value")

    with pytest.raises(ValueError, match="Unsupported generation model") as error:
        make_model("secret-shaped-model-value")

    assert "secret-shaped-model-value" not in str(error.value)


@pytest.mark.parametrize("model_id", ["gemini-3.5-flash-lite", "gemini-3.8-flash"])
def test_allowed_model_uses_google_provider(monkeypatch, model_id):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "fixture-key")

    model = make_model(model_id)

    assert isinstance(model, GoogleModel)
    assert model.model_name == model_id
    assert model.system == "google"
    assert "fixture-key" not in repr(model)


def test_context_checks_combined_budget():
    check_context(9, 1, 10)
    with pytest.raises(ContextLimitError):
        check_context(9, 2, 10)


def test_aggregate_distinguishes_zero_and_partial_input_and_output():
    records = [
        UsageRecord(input_tokens=0, output_tokens=5, details={"thoughts_tokens": 1, "cached_content_tokens": 0}),
        UsageRecord(input_tokens=4, details={"thoughts_tokens": 2}),
    ]

    assert sum_usage(records) == UsageRecord(
        input_tokens=4,
        details={"thoughts_tokens": 3},
    )


def test_aggregate_never_presents_incomplete_counts_as_totals():
    assert sum_usage([]) == UsageRecord()
    assert sum_usage([UsageRecord(), UsageRecord(input_tokens=3, output_tokens=4)]) == UsageRecord()
    assert sum_usage([UsageRecord(input_tokens=0, output_tokens=0)]) == UsageRecord(input_tokens=0, output_tokens=0)


def _fake_google(monkeypatch, *responses):
    requests = []
    responses = iter(responses)

    def respond(request):
        requests.append(json.loads(request.content))
        status, payload = next(responses)
        return httpx2.Response(status, json=payload)

    transport = httpx2.MockTransport(respond)

    def provider(**kwargs):
        return GoogleProvider(http_client=httpx2.AsyncClient(transport=transport, timeout=30), **kwargs)

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(model_runtime, "GoogleProvider", provider)
    return requests


def _response(answer='{"decision":"ok"}', **usage):
    payload = {
        "candidates": [{
            "content": {"role": "model", "parts": [{"text": answer}]},
            "finishReason": "STOP",
        }],
        "modelVersion": "gemini-3.5-flash-lite",
    }
    if usage:
        payload["usageMetadata"] = usage
    return 200, payload


def _prompt(request):
    return json.loads(request["contents"][0]["parts"][0]["text"])


@pytest.mark.parametrize(("mode", "scope"), [
    ("batch", "together"),
    ("per_requirement", "requirement targeted"),
    ("per_case", "single case"),
])
def test_output_mode_keeps_every_requirement_in_the_google_payload(monkeypatch, requirements, mode, scope):
    requests = _fake_google(monkeypatch, _response(promptTokenCount=11, candidatesTokenCount=4))
    runtime = ModelRuntime("gemini-3.5-flash-lite", output_tokens=25)

    answer = asyncio.run(runtime.run(
        "generate", "Generate a bookmark test.", requirements, Answer,
        extra={"output_mode": mode, "target": "R1"},
    ))

    assert answer == Answer(decision="ok")
    assert _prompt(requests[0]) == {
        **requirements.model_dump(),
        "extra": {"output_mode": mode, "target": "R1"},
    }
    assert any(scope in part["text"] for part in requests[0]["systemInstruction"]["parts"])
    assert requests[0]["generationConfig"]["maxOutputTokens"] == 25
    assert requests[0]["generationConfig"]["responseMimeType"] == "application/json"
    record, = runtime.call_records
    assert record.stage == "generate"
    assert record.status == "succeeded"
    assert record.context.requirements_tokens > 0
    assert record.context.instructions_tokens > 0
    assert record.context.schema_tokens > 0
    assert record.context.history_tokens == 0
    assert record.context.output_tokens == 25
    assert runtime.usage_records == [UsageRecord(input_tokens=11, output_tokens=4)]


def test_context_drops_only_explicitly_optional_history(monkeypatch, requirements):
    requests = _fake_google(monkeypatch, _response())
    runtime = ModelRuntime("gemini-3.5-flash-lite", context_limit=800, output_tokens=25)
    extra = {"history": ["old candidate " * 1000], "feedback": "Keep full feedback."}

    asyncio.run(runtime.run("revise", "Revise the case.", requirements, Answer, extra=extra))

    assert _prompt(requests[0]) == {
        **requirements.model_dump(),
        "extra": {"feedback": "Keep full feedback."},
    }
    assert extra["history"]
    record, = runtime.call_records
    assert record.history_dropped
    assert record.context.history_tokens == 0
    assert runtime.usage_records == [UsageRecord()]


def test_context_overflow_refuses_dispatch_without_truncating_requirements(monkeypatch, requirements):
    requests = _fake_google(monkeypatch)
    runtime = ModelRuntime("gemini-3.5-flash-lite", context_limit=65, output_tokens=25)
    before = requirements.model_dump()

    with pytest.raises(ContextLimitError):
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert requirements.model_dump() == before
    assert requests == []
    assert runtime.usage_records == []
    record, = runtime.call_records
    assert record.status == "context_exceeded"
    assert record.context.requirements_tokens > 0


def test_reference_collections_in_nested_extras_are_refused(monkeypatch, requirements):
    requests = _fake_google(monkeypatch)
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    with pytest.raises(ValueError, match="Reference cases"):
        asyncio.run(runtime.run(
            "review", "Review the case.", requirements, Answer,
            extra={"history": [{"reference_cases": [{"id": "secret-reference"}]}]},
        ))

    assert requests == []


def test_serialized_reference_case_in_stage_data_is_refused(monkeypatch, requirements):
    requests = _fake_google(monkeypatch)
    runtime = ModelRuntime("gemini-3.5-flash-lite")
    reference = ReferenceCase(
        id="held-back",
        title="Held-back title",
        description="Held-back description",
        requirement_ids=["R1"],
        source="fixture",
        link_method="explicit",
        link_status="verified",
    )

    with pytest.raises(ValueError, match="Reference cases"):
        asyncio.run(runtime.run(
            "review", "Review the case.", requirements, Answer,
            extra={"cases": [reference.model_dump()]},
        ))

    assert requests == []


def test_provider_usage_retains_zero_and_missing_counters(monkeypatch, requirements):
    _fake_google(monkeypatch, _response(
        promptTokenCount=0, thoughtsTokenCount=3, cachedContentTokenCount=0,
        promptTokensDetails=[{"modality": "TEXT", "tokenCount": 0}],
    ))
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert runtime.usage_records == [
        UsageRecord(
            input_tokens=0,
            details={"thoughts_tokens": 3, "cached_content_tokens": 0, "text_prompt_tokens": 0},
        ),
    ]


def test_output_retry_keeps_requirements_and_usage_from_rejected_response(monkeypatch, requirements):
    requests = _fake_google(
        monkeypatch,
        _response(answer='{"wrong":"field"}', promptTokenCount=14, candidatesTokenCount=2),
        _response(promptTokenCount=30),
    )
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    assert asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer)) == Answer(decision="ok")

    assert len(requests) == 2
    assert [_prompt(request)["requirements"] for request in requests] == [requirements.model_dump()["requirements"]] * 2
    assert [record.status for record in runtime.call_records] == ["retry", "succeeded"]
    assert runtime.call_records[1].context.history_tokens > 0
    assert runtime.usage_records == [
        UsageRecord(input_tokens=14, output_tokens=2),
        UsageRecord(input_tokens=30),
    ]


def test_retry_context_overflow_keeps_only_provider_usage_for_dispatched_attempt(monkeypatch, requirements):
    requests = _fake_google(monkeypatch, _response(answer="x" * 4000, promptTokenCount=12, candidatesTokenCount=80))
    runtime = ModelRuntime("gemini-3.5-flash-lite", context_limit=800, output_tokens=30)

    with pytest.raises(ContextLimitError):
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert len(requests) == 1
    assert [record.status for record in runtime.call_records] == ["retry", "context_exceeded"]
    assert [record.attempt for record in runtime.call_records] == [1, 2]
    assert len({record.call_id for record in runtime.call_records}) == 1
    assert runtime.usage_records == [UsageRecord(input_tokens=12, output_tokens=80)]


def test_provider_error_has_unavailable_usage_without_persisting_error_body(monkeypatch, requirements):
    requests = _fake_google(monkeypatch, (403, {"error": {
        "code": 403, "status": "PERMISSION_DENIED", "message": "private error body",
    }}))
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    with pytest.raises(ModelHTTPError):
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert len(requests) == 1
    assert runtime.usage_records == [UsageRecord()]
    record, = runtime.call_records
    assert record.status == "failed"
    assert record.error_type == "ModelAuthenticationError"
    assert "private error body" not in record.model_dump_json()


def test_exhausted_validation_keeps_usage_for_failed_call(monkeypatch, requirements):
    _fake_google(monkeypatch, _response(answer="{}", promptTokenCount=7, candidatesTokenCount=2))
    runtime = ModelRuntime("gemini-3.5-flash-lite", retries=0)

    with pytest.raises(UnexpectedModelBehavior):
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    record, = runtime.call_records
    assert record.status == "failed"
    assert runtime.usage_records == [UsageRecord(input_tokens=7, output_tokens=2)]


def test_continuation_is_refused_after_one_audited_provider_request(monkeypatch, requirements):
    status, partial = _response(promptTokenCount=12, candidatesTokenCount=2)
    partial["candidates"][0].update(
        finishReason="CONTINUATION",
        continuationToken="Y2hlY2twb2ludA==",
    )
    requests = _fake_google(monkeypatch, (status, partial), _response(answer=" "))
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    with pytest.raises(UnexpectedModelBehavior, match="continuation"):
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert len(requests) == 1
    assert _prompt(requests[0])["requirements"] == requirements.model_dump()["requirements"]
    assert runtime.usage_records == [UsageRecord(input_tokens=12, output_tokens=2)]
    record, = runtime.call_records
    assert record.status == "failed"
    assert record.usage == runtime.usage_records[0]


@pytest.mark.parametrize("nested", [False, True])
def test_http_error_retains_structured_usage_metadata(monkeypatch, requirements, nested):
    payload = {"error": {"code": 400, "status": "INVALID_ARGUMENT"}}
    container = payload["error"] if nested else payload
    container["usageMetadata"] = {"promptTokenCount": 13, "candidatesTokenCount": 0}
    requests = _fake_google(monkeypatch, (400, payload))
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    with pytest.raises(ModelHTTPError):
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert len(requests) == 1
    assert runtime.usage_records == [UsageRecord(input_tokens=13, output_tokens=0)]
    assert runtime.call_records[0].status == "failed"


def test_http_error_hides_credentials_and_provider_exception_chain(monkeypatch, requirements):
    credential = "test-key"
    _fake_google(monkeypatch, (403, {"error": {
        "code": 403,
        "status": "PERMISSION_DENIED",
        "message": f"Authorization echoed {credential}",
    }}))
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    with pytest.raises(ModelAuthenticationError) as failure:
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    error = failure.value
    assert isinstance(error, ModelHTTPError)
    assert error.status_code == 403
    assert error.model_name == "gemini-3.5-flash-lite"
    assert error.body is None
    assert error.headers is None
    assert error.__cause__ is None
    assert error.__context__ is None
    assert credential not in str(error)
    assert credential not in repr(error)
    assert credential not in "".join(traceback.format_exception(error))


def test_failed_output_validation_hides_provider_data_in_traceback(monkeypatch, requirements):
    credential = "test-key"
    _fake_google(monkeypatch, _response(
        answer=json.dumps({"unexpected": credential}), promptTokenCount=17, candidatesTokenCount=3,
    ))
    runtime = ModelRuntime("gemini-3.5-flash-lite", retries=0)

    with pytest.raises(UnexpectedModelBehavior) as failure:
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    error = failure.value
    assert error.__cause__ is None
    assert error.__context__ is None
    assert credential not in "".join(traceback.format_exception(error))
    assert runtime.usage_records == [UsageRecord(input_tokens=17, output_tokens=3)]


@pytest.mark.parametrize("unexpected_metadata", [
    {"futureUsageField": {"version": 2}},
    {"thoughtsTokenCount": "invalid"},
    {"thoughtsTokenCount": True, "cachedContentTokenCount": 2.0, "totalTokenCount": -1},
])
def test_http_usage_keeps_valid_counts_when_optional_metadata_is_unusable(
    monkeypatch, requirements, unexpected_metadata,
):
    _fake_google(monkeypatch, (400, {
        "error": {"code": 400, "status": "INVALID_ARGUMENT"},
        "usageMetadata": {
            "promptTokenCount": 13,
            "candidatesTokenCount": 0,
            "toolUsePromptTokenCount": 1,
            **unexpected_metadata,
        },
    }))
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    with pytest.raises(ModelHTTPError) as failure:
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert failure.value.status_code == 400
    assert runtime.usage_records == [
        UsageRecord(input_tokens=13, output_tokens=0, details={"tool_use_prompt_tokens": 1}),
    ]


@pytest.mark.parametrize("unrecognized_modality", ["fixture-canary-key", 17])
def test_http_usage_audits_only_known_modalities(monkeypatch, requirements, recwarn, unrecognized_modality):
    _fake_google(monkeypatch, (400, {
        "error": {"code": 400, "status": "INVALID_ARGUMENT"},
        "usageMetadata": {
            "promptTokenCount": 13,
            "promptTokensDetails": [
                {"modality": unrecognized_modality, "tokenCount": 3},
                {"modality": "text", "tokenCount": 0},
                {"modality": "AUDIO", "tokenCount": True},
            ],
        },
    }))
    monkeypatch.setenv("GOOGLE_API_KEY", "fixture-canary-key")
    runtime = ModelRuntime("gemini-3.5-flash-lite")

    with pytest.raises(ModelHTTPError) as failure:
        asyncio.run(runtime.run("generate", "Write cases.", requirements, Answer))

    assert failure.value.status_code == 400
    assert failure.value.__cause__ is None
    assert failure.value.__context__ is None
    assert "fixture-canary-key" not in "".join(traceback.format_exception(failure.value))
    assert "fixture-canary-key" not in runtime.call_records[0].model_dump_json()
    assert list(recwarn) == []
    assert runtime.usage_records == [
        UsageRecord(input_tokens=13, details={"text_prompt_tokens": 0}),
    ]
