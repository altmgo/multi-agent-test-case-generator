"""Run optional multiagent checkpoints under one bounded revision budget."""

from asyncio import CancelledError

from pydantic import JsonValue

from model_runtime import Runtime
from schemas import AgentOpinion, CandidateAssessment, GenerationInput, GenerationResult

from .. import GenerationCancelled
from .analyst import analyze
from .coverage import E2EDevCalibrationProfile, review_coverage
from .critic import critique
from .generator import InvalidCaseSet, generate
from .selection import decide_round, score_assessment
from .state import (
    CANDIDATES_PER_ROUND,
    PROMPT_VERSION,
    STAGE_ERRORS,
    Attempt,
    Control,
    Failure,
    MultiagentFailure,
    OutputMode,
    PendingRevision,
    RunTrace,
    StageRunner,
)
from .validator import validate

_CONTROLS = {"critic": critique, "validator": validate}
_OPTIONAL_AGENTS = {*_CONTROLS, "analyst", "coverage"}


async def _control(runner: StageRunner, attempt: Attempt, name: Control) -> AgentOpinion:
    opinion = await _CONTROLS[name](runner, attempt.assessment)
    attempt.assessment.opinions.append(opinion)
    score_assessment(attempt.assessment)
    return opinion


async def _attempt(
    runner: StageRunner,
    attempt: Attempt,
    analyst_enabled: bool,
    output_mode: OutputMode,
    revision: dict[str, JsonValue] | None = None,
    controls: tuple[Control, ...] = (),
) -> None:
    stage = "analyst"
    try:
        if analyst_enabled:
            attempt.analysis = await analyze(runner, attempt.assessment.candidate_id, revision)
        stage = "generator"
        await generate(runner, attempt, output_mode, revision)
        score_assessment(attempt.assessment)
        for name in controls:
            stage = name
            await _control(runner, attempt, name)
    except STAGE_ERRORS as error:
        attempt.assessment.valid = False
        attempt.failure = Failure(
            stage=stage,
            error_type=type(error).__name__,
            detail=str(error) if isinstance(error, InvalidCaseSet) else None,
        )


async def run_multiagent(
    input: GenerationInput,
    runtime: Runtime,
    enabled: set[str],
    max_rounds: int,
    *,
    output_mode: OutputMode = "batch",
    calibration_profile: E2EDevCalibrationProfile | None = None,
) -> GenerationResult:
    """Return generation and revision data, or raise with a persistable partial result."""
    if unknown := enabled - _OPTIONAL_AGENTS:
        raise ValueError("Unknown optional multiagent agents: " + ", ".join(sorted(unknown)))
    if max_rounds < 0:
        raise ValueError("Multiagent max_rounds must be nonnegative")
    if output_mode not in {"batch", "per_requirement", "per_case"}:
        raise ValueError(f"Unsupported Multiagent output mode: {output_mode}")
    if calibration_profile is not None:
        if not isinstance(calibration_profile, E2EDevCalibrationProfile):
            raise TypeError("Multiagent calibration_profile requires an E2EDevCalibrationProfile")
        calibration_profile = E2EDevCalibrationProfile.model_validate(calibration_profile)

    initial = Attempt(assessment=CandidateAssessment(candidate_id="initial", cases=[]))
    controls = tuple(name for name in _CONTROLS if name in enabled)
    trace = RunTrace(initial=initial, pending_controls=list(controls))
    runner = StageRunner(input, runtime, trace.calls)
    try:
        await _orchestrate(runner, trace, controls, enabled, max_rounds, output_mode, calibration_profile)
    except CancelledError as error:
        stage = trace.calls[-1].stage if trace.calls else "generation"
        trace.status = "failed"
        trace.failure = Failure(stage=stage, error_type=type(error).__name__)
        if trace.accepted_assessment is None:
            initial.assessment.valid = False
            initial.failure = trace.failure
        raise GenerationCancelled(error, stage, trace.result()) from None
    return trace.result()


async def _orchestrate(
    runner: StageRunner,
    trace: RunTrace,
    controls: tuple[Control, ...],
    enabled: set[str],
    max_rounds: int,
    output_mode: OutputMode,
    calibration_profile: E2EDevCalibrationProfile | None,
) -> None:
    initial = trace.initial
    analyst_enabled = "analyst" in enabled
    await _attempt(runner, initial, analyst_enabled, output_mode)
    if initial.failure is not None:
        trace.status = "failed"
        trace.failure = initial.failure
        raise MultiagentFailure(trace.failure, trace.result())

    accepted = initial
    trace.accept(accepted)
    attempts = [initial]
    stopped_at: dict[Control, str] = {}

    for index, requester in enumerate(controls):
        try:
            opinion = await _control(runner, accepted, requester)
        except STAGE_ERRORS as error:
            trace.status = "failed"
            trace.failure = Failure(stage=requester, error_type=type(error).__name__)
            break
        while opinion.request_revision and len(trace.rounds) < max_rounds:
            number = len(trace.rounds) + 1
            baseline = accepted.assessment
            revision = {
                "accepted_id": baseline.candidate_id,
                "requester": requester,
                "cases": [case.model_dump(mode="json") for case in baseline.cases],
                "analysis": accepted.analysis.model_dump(mode="json") if accepted.analysis else None,
                "feedback": [item.model_dump(mode="json") for item in baseline.opinions],
            }
            candidates = []
            for position in range(1, CANDIDATES_PER_ROUND + 1):
                candidate = Attempt(
                    assessment=CandidateAssessment(candidate_id=f"round-{number}-candidate-{position}", cases=[])
                )
                await _attempt(runner, candidate, analyst_enabled, output_mode, revision, controls[: index + 1])
                candidates.append(candidate)
            attempts.extend(candidates)
            decision = await decide_round(runner, number, requester, accepted, candidates)
            trace.rounds.append(decision)
            if decision.monotonicity == "unverified":
                trace.monotonicity = "unverified"
            if decision.selected_id == baseline.candidate_id:
                stopped_at[requester] = baseline.candidate_id
                break
            accepted = next(candidate for candidate in candidates if candidate.assessment.candidate_id == decision.selected_id)
            trace.accept(accepted)
            opinion = accepted.assessment.opinions[-1]
        trace.pending_controls.pop(0)

    completed_controls = controls[: len(controls) - len(trace.pending_controls)]
    for requester, opinion in zip(completed_controls, accepted.assessment.opinions, strict=True):
        if opinion.request_revision:
            if len(trace.rounds) == max_rounds:
                reason = "round_limit"
            elif stopped_at.get(requester) == trace.accepted_id:
                reason = "no_improvement"
            else:
                reason = "checkpoint_passed"
            trace.pending.append(
                PendingRevision(agent=requester, candidate_id=trace.accepted_id, opinion=opinion, reason=reason)
            )

    if trace.failure is not None:
        raise MultiagentFailure(trace.failure, trace.result())

    if "coverage" in enabled:
        try:
            trace.coverage = await review_coverage(runner, accepted, attempts, calibration_profile)
        except STAGE_ERRORS as error:
            trace.coverage_failure = Failure(stage="coverage", error_type=type(error).__name__)
