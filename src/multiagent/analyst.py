"""Identify testable behavior and uncertainty across the full requirement set."""

from pydantic import JsonValue

from .state import Analysis, StageRunner


async def analyze(
    runner: StageRunner, attempt_id: str, revision: dict[str, JsonValue] | None
) -> Analysis:
    context = None
    if revision is not None:
        context = {
            key: value for key, value in revision.items() if key != "cases"
        }
    return await runner.call(
        "analyst",
        attempt_id,
        "Decompose every requirement into distinct normal, edge, boundary, and abnormal scenarios. "
        "Use concrete values and UI identifiers only when they come from the supplied requirements. "
        "For each requirement, separate scenarios that are already represented in the accepted cases "
        "from actionable missing scenarios. For revisions, address feedback on the accepted state. "
        "Do not invent unsupported behavior. Return concise findings grouped by requirement ID. "
        "Focus on scenario distinctions that can become one testable high-level case.",
        Analysis,
        revision=context,
    )
