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
        "Identify testable behavior, boundaries, normal and abnormal paths, and ambiguities. "
        "Use every requirement. For revisions, address feedback on the accepted state. "
        "Return concise findings grouped by requirement ID. Focus on actionable conditions and gaps.",
        Analysis,
        revision=context,
    )
