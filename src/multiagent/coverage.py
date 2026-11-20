"""Advisory coverage based on requirements and generated cases."""

from .state import Attempt, CoverageReport, StageRunner

async def review_coverage(
    runner: StageRunner,
    accepted: Attempt,
    attempts: list[Attempt],
) -> CoverageReport:
    index: dict[str, list[dict]] = {"accepted": [], "rejected": []}
    for attempt in attempts:
        assessment = attempt.assessment
        status = "accepted" if attempt is accepted else "rejected"
        fields = {"id", "title", "requirement_ids"} if status == "rejected" else None
        index[status].extend(
            {"candidate_id": assessment.candidate_id, **case.model_dump(mode="json", include=fields)}
            for case in assessment.cases
        )
    return await runner.call(
        "coverage",
        accepted.assessment.candidate_id,
        "Compare accepted cases against every supplied requirement and identify concrete missing scenarios. "
        "Classify each gap as normal, edge, abnormal, boundary, or other. Include only behaviors that are "
        "explicitly supported by the requirement text or a supplied UI identifier. Do not invent actions, "
        "products, expected values, or error behavior not grounded in the requirements. Also identify excess "
        "or repetitive cases. Use rejected cases as context only.",
        CoverageReport,
        case_index=index,
    )
