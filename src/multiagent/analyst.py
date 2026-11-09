"""Identify testable behavior and uncertainty across the full requirement set."""

from pydantic import JsonValue

from .state import Analysis, StageRunner


async def analyze(
    runner: StageRunner, attempt_id: str, revision: dict[str, JsonValue] | None
) -> Analysis:
    return await runner.call(
        "analyst",
        attempt_id,
        "Identify testable behavior, boundaries, normal and abnormal paths, and ambiguities. "
        "Use every requirement. For revisions, address feedback on the accepted state. "
        "Return a concise analysis grounded in the supplied requirements.",
        Analysis,
        revision=revision,
    )
