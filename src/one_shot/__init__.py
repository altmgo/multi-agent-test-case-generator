"""Single-call high-level test case generation."""

from pydantic import BaseModel

from src.tcg.runtime import Runtime, sum_usage
from src.tcg.schemas import GeneratedCase, GenerationInput, GenerationResult, UsageRecord, validate_cases

PROMPT_VERSION = "one-shot-v1"


class _CaseBatch(BaseModel):
    cases: list[GeneratedCase]


async def generate_one_shot(input: GenerationInput, runtime: Runtime) -> GenerationResult:
    """Generate a batch from the complete requirement set in exactly one call."""
    before = len(runtime.usage_records)
    answer = await runtime.run(
        "one_shot",
        "Generate high-level test cases from all requirements. Include normal and abnormal cases. "
        "Each case must cite only supplied requirement IDs.",
        input,
        _CaseBatch,
        extra={"output_mode": "batch", "prompt_version": PROMPT_VERSION},
    )
    validate_cases(input, answer.cases)
    cases = [case.model_copy(update={"id": f"G-{index:03d}"}) for index, case in enumerate(answer.cases, 1)]
    return GenerationResult(
        cases=cases,
        usage=sum_usage(runtime.usage_records[before:]),
        prompt_version=PROMPT_VERSION,
    )
