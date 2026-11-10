"""Multiagent attempts, selection decisions, and per-stage audit data."""

from asyncio import CancelledError
from copy import deepcopy
from typing import Literal, TypeVar

from pydantic import BaseModel, Field, JsonValue
from pydantic_ai.exceptions import ModelAPIError, UnexpectedModelBehavior

from tcg.runtime import Runtime, sum_usage
from tcg.schemas import AgentOpinion, CandidateAssessment, GenerationInput, GenerationResult, UsageRecord

PROMPT_VERSION = "multiagent-v1"
CANDIDATES_PER_ROUND = 3
STAGE_ERRORS = (ValueError, ModelAPIError, UnexpectedModelBehavior)
Control = Literal["critic", "validator"]
OutputMode = Literal["batch", "per_requirement", "per_case"]
Comparison = Literal["improves", "ties", "worse", "invalid", "incompatible", "unassessed"]
Monotonicity = Literal["confirmed", "unverified"]
T = TypeVar("T", bound=BaseModel)


class Analysis(BaseModel):
    analysis: str


class ControlOutput(BaseModel):
    feedback: str
    request_revision: bool
    confirmed_blockers: list[str]
    blocker_assessment_complete: bool = True


class Failure(BaseModel):
    stage: str
    error_type: str
    detail: str | None = None


class Attempt(BaseModel):
    assessment: CandidateAssessment
    analysis: Analysis | None = None
    failure: Failure | None = None


class CandidateDecision(BaseModel):
    attempt: Attempt
    comparison: Comparison


class PendingRevision(BaseModel):
    agent: Control
    candidate_id: str
    opinion: AgentOpinion
    reason: Literal["round_limit", "no_improvement", "checkpoint_passed"]


class QualitativeJudgment(BaseModel):
    candidate_id: str
    comparison: Literal["improves", "ties", "worse"]


class QualitativeRanking(BaseModel):
    preferred_id: str | None
    rationale: str = Field(min_length=1)
    judgments: list[QualitativeJudgment]


class RevisionRound(BaseModel):
    number: int
    requester: Control
    accepted_before: CandidateAssessment
    candidates: list[CandidateDecision]
    selected_id: str
    decision: Literal["preserved", "objective", "qualitative"]
    qualitative: QualitativeRanking | None = None
    failure: Failure | None = None
    monotonicity: Monotonicity


class StageCall(BaseModel):
    stage: str
    subject_id: str
    output: JsonValue = None
    error_type: str | None = None
    usage: list[UsageRecord] = Field(default_factory=list)


class CoverageReport(BaseModel):
    feedback: str


class RunTrace(BaseModel):
    initial: Attempt
    rounds: list[RevisionRound] = Field(default_factory=list)
    status: Literal["completed", "failed"] = "completed"
    failure: Failure | None = None
    accepted_id: str | None = None
    accepted_assessment: CandidateAssessment | None = None
    pending: list[PendingRevision] = Field(default_factory=list)
    pending_controls: list[Control] = Field(default_factory=list)
    coverage: CoverageReport | None = None
    coverage_failure: Failure | None = None
    calls: list[StageCall] = Field(default_factory=list)
    monotonicity: Monotonicity = "confirmed"

    def accept(self, attempt: Attempt) -> None:
        self.accepted_id = attempt.assessment.candidate_id
        self.accepted_assessment = attempt.assessment

    def result(self) -> GenerationResult:
        return GenerationResult(
            cases=self.accepted_assessment.cases if self.accepted_assessment is not None else [],
            usage=sum_usage([usage for call in self.calls for usage in call.usage]),
            prompt_version=PROMPT_VERSION,
            trace=self.model_dump(mode="json"),
        )


class MultiagentFailure(RuntimeError):
    """A fatal stage failed after the run began, with a persistable partial result."""

    def __init__(self, failure: Failure, partial_result: GenerationResult):
        super().__init__(f"Multiagent {failure.stage} failed ({failure.error_type})")
        self.partial_result = partial_result


class StageRunner:
    def __init__(self, input: GenerationInput, runtime: Runtime, calls: list[StageCall]):
        self.input = input.model_copy(deep=True)
        self.runtime = runtime
        self.calls = calls

    async def call(
        self,
        stage: str,
        subject_id: str,
        instructions: str,
        output_type: type[T],
        **extra: JsonValue,
    ) -> T:
        call = StageCall(stage=stage, subject_id=subject_id)
        self.calls.append(call)
        usage_start = len(self.runtime.usage_records)
        try:
            output = await self.runtime.run(
                f"multiagent_{stage}",
                instructions,
                self.input.model_copy(deep=True),
                output_type,
                extra={"prompt_version": PROMPT_VERSION, **deepcopy(extra)},
            )
        except (CancelledError, *STAGE_ERRORS) as error:
            call.error_type = type(error).__name__
            raise
        else:
            call.output = output.model_dump(mode="json")
            return output
        finally:
            call.usage = self.runtime.usage_records[usage_start:]
