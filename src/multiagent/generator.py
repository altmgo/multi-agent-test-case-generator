"""Generate a complete proposed case set from requirements and any analysis."""

from pydantic import BaseModel, JsonValue

from tcg.schemas import GeneratedCase, validate_cases

from .state import Attempt, OutputMode, StageRunner


MAX_CASES_PER_REQUIREMENT = 2


class CaseBatch(BaseModel):
    cases: list[GeneratedCase]


class InvalidCaseSet(ValueError):
    """A structured proposal violates the case or output scope contract."""


async def generate(
    runner: StageRunner,
    attempt: Attempt,
    output_mode: OutputMode,
    revision: dict[str, JsonValue] | None,
) -> None:
    assessment = attempt.assessment
    analysis = attempt.analysis.model_dump(mode="json") if attempt.analysis else None
    if revision is not None and analysis is not None:
        revision = {key: value for key, value in revision.items() if key != "analysis"}
    targets = [None] if output_mode == "batch" else [item.id for item in runner.input.requirements]
    for target in targets:
        answer = await runner.call(
            "generator",
            assessment.candidate_id,
            "Generate high-level test cases with clear expected behavior and links only to supplied IDs. "
            "Use the full requirements and any analysis. Decompose each requirement into distinct normal, "
            "boundary, edge, and abnormal scenarios when supported by the requirement text or supplied UI "
            "identifiers. Return at most two focused cases for each targeted requirement. Prefer normal and "
            "highest-risk supported scenarios over speculative variants. Keep each scenario non-repetitive. "
            "Do not invent unsupported actions, "
            "values, or outcomes. For revisions, replace the accepted set with a complete grounded set that "
            "closes the reported coverage gaps while preserving the precision of existing sound cases.",
            CaseBatch,
            analysis=analysis,
            revision=revision,
            output_mode=output_mode,
            target=target,
        )
        for case in answer.cases:
            stable_id = f"G-{len(assessment.cases) + 1:03d}"
            assessment.cases.append(case.model_copy(update={"id": stable_id}, deep=True))
        try:
            validate_cases(runner.input, answer.cases)
        except ValueError as error:
            raise InvalidCaseSet(str(error)) from None
        if target is not None and any(target not in case.requirement_ids for case in answer.cases):
            raise InvalidCaseSet(f"Generated cases must link to their scoped requirement {target!r}")
        if target is not None and len(answer.cases) > MAX_CASES_PER_REQUIREMENT:
            raise InvalidCaseSet(
                f"Generated cases for scoped requirement {target!r} exceed "
                f"the limit of {MAX_CASES_PER_REQUIREMENT}"
            )
        if output_mode == "per_case" and len(answer.cases) > 1:
            raise InvalidCaseSet("per_case output returned more than one case for a call")
