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
        "Advise on coverage gaps, excess, overgeneration, and repetition in the accepted cases. "
        "Flag cases that test speculative or unstated behaviors not grounded in the requirement text as excess. "
        "For each requirement, check whether the accepted cases cover what is explicitly described in the requirement "
        "without generating redundant or fabricated edge/error cases. List missing requirements or explicit scenario types "
        "as gaps. Use rejected cases as context only. Compare coverage against the supplied requirements. "
        "Return feedback only.",
        CoverageReport,
        case_index=index,
    )
