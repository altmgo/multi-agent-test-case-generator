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
        index[status].extend(
            {"candidate_id": assessment.candidate_id, **case.model_dump(mode="json")}
            for case in assessment.cases
        )
    return await runner.call(
        "coverage",
        accepted.assessment.candidate_id,
        "Advise on coverage gaps, excess, and repetition in the accepted cases. Use rejected cases "
        "as context only. Compare coverage against the supplied requirements. Return feedback only.",
        CoverageReport,
        case_index=index,
    )
