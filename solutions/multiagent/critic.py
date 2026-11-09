"""Critique scenario quality using a common blocker rubric."""

from schemas import AgentOpinion, CandidateAssessment

from .selection import REVIEW_RUBRIC
from .state import ControlOutput, StageRunner


async def critique(runner: StageRunner, assessment: CandidateAssessment) -> AgentOpinion:
    answer = await runner.call(
        "critic",
        assessment.candidate_id,
        "Critique the proposed high-level cases for testability, distinct scenarios, and risk. "
        + REVIEW_RUBRIC,
        ControlOutput,
        cases=[case.model_dump(mode="json") for case in assessment.cases],
    )
    return AgentOpinion(agent="critic", **answer.model_dump())
