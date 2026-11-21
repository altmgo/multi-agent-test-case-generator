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
        "Use every requirement. For each requirement, identify whether it describes only a single straightforward "
        "acceptance criterion or multiple distinct behaviors. Only list distinct scenario types (Edge, Boundary, "
        "Abnormal/Error) if the requirement text explicitly mentions conditions, parameters, or failure paths for them. "
        "Never invent hypothetical edge cases, corrupted states, or negative scenarios not mentioned in the requirement. "
        "If a requirement is a simple declaration (e.g. menu presence, display existence), specify that only a single Normal "
        "test scenario is warranted. "
        "For revisions, address feedback on the accepted state and mark each scenario type as covered or missing. "
        "Return concise findings grouped by requirement ID. Focus on actionable conditions and gaps.",
        Analysis,
        revision=context,
    )
