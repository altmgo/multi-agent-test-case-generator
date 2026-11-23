"""Critique scenario quality using a common blocker rubric."""

from tcg.schemas import AgentOpinion, CandidateAssessment

from .selection import REVIEW_RUBRIC
from .state import ControlOutput, StageRunner


async def critique(runner: StageRunner, assessment: CandidateAssessment) -> AgentOpinion:
    answer = await runner.call(
        "critic",
        assessment.candidate_id,
        "Critique the proposed high-level cases for testability, explicit scenario coverage, distinct scenarios, "
        "and risk. Compare the supplied requirements against the cases before deciding whether revision is needed. "
        "Do not merely assert that coverage is complete. For every requirement, list its explicitly described "
        "Normal/Edge/Boundary/Abnormal/Error behaviors and name the matching case for each behavior. "
        "If any explicit behavior has no matching case, set request_revision=true and identify the exact requirement "
        "ID and missing behavior in feedback. Generic impressions of coverage are insufficient evidence. "
        + REVIEW_RUBRIC,
        ControlOutput,
        cases=[case.model_dump(mode="json") for case in assessment.cases],
    )
    payload = answer.model_dump()
    if gaps := payload["missing_scenario_gaps"]:
        payload["request_revision"] = True
        gap_text = "; ".join(gaps)
        payload["feedback"] = (
            f"{payload['feedback']} Missing explicit scenarios: {gap_text}"
        ).strip()
    return AgentOpinion(agent="critic", **payload)
