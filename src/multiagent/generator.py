"""Generate a complete proposed case set from requirements and any analysis."""

from pydantic import BaseModel, JsonValue

from tcg.schemas import GeneratedCase, validate_cases

from .state import Attempt, OutputMode, StageRunner


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
            "Generate concise, high-level test cases with clear expected behavior and links only to supplied IDs. "
            "Ground every test strictly and directly in the explicit requirement text and any analysis. "
            "Do NOT invent speculative, hypothetical, or unstated conditions (such as missing files, network errors, "
            "corrupted assets, window resizing, or boundary placements) unless explicitly mentioned in the requirement text. "
            "If a requirement is simple (e.g., verifying a menu item, theme existence, or UI element presence), "
            "generate exactly one focused normal case for it. "
            "For requirements with multiple explicitly described atomic behaviors, generate a complete set that has "
            "one distinct, focused case for each named action or state transition (for example, select and deselect "
            "are separate behaviors; add and delete are separate behaviors; edit mode and view mode are separate behaviors). "
            "For persistence requirements, cover both the normal saved state and the explicitly described empty or "
            "restored state when each is stated. "
            "Only generate additional scenario types (Edge, Boundary, Error) if the requirement text explicitly "
            "defines multiple distinct operations, parameters, ranges, or error conditions. "
            "Avoid redundant or overlapping test cases. "
            "For revisions, use the accepted cases and feedback to generate a complete replacement for "
            "the requested scope, keeping sound coverage.",
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
        if output_mode == "per_case" and len(answer.cases) > 1:
            raise InvalidCaseSet("per_case output returned more than one case for a call")
