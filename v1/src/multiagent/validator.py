"""Validate case grounding and traceability against the supplied requirements."""

from schemas import AgentOpinion, CandidateAssessment

from .selection import REVIEW_RUBRIC
from .state import ControlOutput, StageRunner


async def validate(runner: StageRunner, assessment: CandidateAssessment) -> AgentOpinion:
    answer = await runner.call(
        "validator",
        assessment.candidate_id,
        "Verify that the cases and expected behavior follow the requirements and their cited IDs. "
        + REVIEW_RUBRIC,
        ControlOutput,
        cases=[case.model_dump(mode="json") for case in assessment.cases],
    )
    return AgentOpinion(agent="validator", **answer.model_dump())
