"""Compare valid candidates against the same accepted state and control scope."""

from tcg.schemas import CandidateAssessment

from .state import (
    Attempt,
    CandidateDecision,
    Comparison,
    Control,
    Failure,
    QualitativeRanking,
    RevisionRound,
    STAGE_ERRORS,
    StageRunner,
)

REVIEW_RUBRIC = (
    "Report each confirmed blocker as a concise, distinct problem grounded in the requirements. "
    "A blocker prevents executing a case, gives unsupported expected behavior, or makes an essential "
    "requirement untestable. Mark blocker_assessment_complete false when evidence is inconclusive. "
    "Before judging blockers, compare every requirement in the supplied input with the proposed cases "
    "requirement by requirement. If a requirement explicitly describes more than one distinct operation, "
    "state transition, parameter, boundary, normal path, or error state, confirm whether there is a "
    "distinct case covering each explicitly described scenario. A missing explicit scenario is a coverage "
    "gap, not a blocker: set request_revision true, explain exactly which requirement and scenario is missing, "
    "and do not request speculative scenarios that are not stated in the requirement. "
    "For a simple declaration or menu/UI-presence requirement, do not request variants unless the text explicitly "
    "defines multiple behaviors or states. "
    "Flag speculative test cases that test unstated behavior, hypothetical errors, or conditions not "
    "supported by the requirement text, as well as redundant cases. "
    "Request revision only for confirmed blocker fixes, confirmed redundant excess, or actionable explicit "
    "coverage gaps; explain each requested change in feedback."
)


def _normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def score_assessment(assessment: CandidateAssessment) -> None:
    blockers = {
        text
        for opinion in assessment.opinions
        for blocker in opinion.confirmed_blockers
        if (text := _normalized(blocker))
    }
    distinct_cases: dict[tuple[str, str], set[str]] = {}
    for case in assessment.cases:
        key = (_normalized(case.title), _normalized(case.description))
        distinct_cases.setdefault(key, set()).update(case.requirement_ids)
    covered = {requirement_id for links in distinct_cases.values() for requirement_id in links}
    assessment.confirmed_blockers = len(blockers)
    assessment.covered_requirements = len(covered)
    assessment.duplicates = len(assessment.cases) - len(distinct_cases)
    assessment.comparable = all(opinion.blocker_assessment_complete for opinion in assessment.opinions)


def _score(assessment: CandidateAssessment) -> tuple[int, int, int, int]:
    distinct_cases = len({
        (_normalized(case.title), _normalized(case.description))
        for case in assessment.cases
    })
    return (
        -assessment.confirmed_blockers,
        distinct_cases,
        assessment.covered_requirements,
        -assessment.duplicates,
    )


def _blocker_count_is_complete(assessment: CandidateAssessment) -> bool:
    return assessment.comparable and all(opinion.blocker_assessment_complete for opinion in assessment.opinions)


def _compare(accepted: CandidateAssessment, candidate: CandidateAssessment) -> Comparison:
    if not candidate.valid:
        return "invalid"
    if [item.agent for item in candidate.opinions] != [item.agent for item in accepted.opinions]:
        return "incompatible"
    if not accepted.valid:
        return "improves"

    accepted_complete = _blocker_count_is_complete(accepted)
    candidate_complete = _blocker_count_is_complete(candidate)
    accepted_score = _score(accepted)
    candidate_score = _score(candidate)
    # With an incomplete blocker review the confirmed count is a lower bound,
    # so the observed lexicographic score is an upper bound.
    if candidate_complete and candidate_score > accepted_score:
        return "improves"
    if accepted_complete and candidate_score < accepted_score:
        return "worse"
    if accepted_complete and candidate_complete:
        return "ties"
    return "unassessed"


def select_candidate(
    accepted: CandidateAssessment, candidates: list[CandidateAssessment]
) -> CandidateAssessment:
    """Choose the highest proven improvement under the same ordered control prefix."""
    improvements = [candidate for candidate in candidates if _compare(accepted, candidate) == "improves"]
    return max(improvements, key=_score, default=accepted)


async def decide_round(
    runner: StageRunner,
    number: int,
    requester: Control,
    accepted: Attempt,
    attempts: list[Attempt],
) -> RevisionRound:
    baseline = accepted.assessment
    candidate_decisions = [
        CandidateDecision(
            attempt=attempt.model_copy(deep=True),
            comparison=_compare(baseline, attempt.assessment),
        )
        for attempt in attempts
    ]
    candidates = [attempt.assessment for attempt in attempts]
    objective = select_candidate(baseline, candidates)
    top = [
        item.attempt.assessment
        for item in candidate_decisions
        if item.comparison == "improves" and _score(item.attempt.assessment) == _score(objective)
    ]
    unresolved = [item for item in candidate_decisions if item.comparison == "unassessed"]
    eligible = [*top, *(item.attempt.assessment for item in unresolved)]
    decision = RevisionRound(
        number=number,
        requester=requester,
        accepted_before=baseline.model_copy(deep=True),
        candidates=candidate_decisions,
        selected_id=objective.candidate_id,
        decision="preserved" if objective is baseline else "objective",
        monotonicity="confirmed",
    )
    if len(top) < 2 and not unresolved:
        return decision

    try:
        ranking = await runner.call(
            "selection",
            f"round-{number}",
            "Apply the same rubric to the accepted state and every supplied candidate. "
            "Favor fewer confirmed blockers, more valid distinct cases, more requirements covered, "
            "and fewer duplicates, in that order. Only count cases that cover explicitly described scenarios. "
            "Where counts leave uncertainty, compare case "
            "grounding, testability and distinct scenarios. Classify every candidate relative to accepted. "
            "Name the best strict improvement if supported and explain your choice. "
            "Preserve accepted if evidence supports a tie, a regression, or no clear improvement.",
            QualitativeRanking,
            accepted=baseline.model_dump(mode="json"),
            candidates=[candidate.model_dump(mode="json") for candidate in eligible],
        )
    except STAGE_ERRORS as error:
        decision.failure = Failure(stage="selection", error_type=type(error).__name__)
        return decision

    decision.qualitative = ranking
    judgments = {}
    for item in ranking.judgments:
        # An ambiguous duplicated verdict supplies no usable evidence.
        judgments[item.candidate_id] = (
            "unassessed" if item.candidate_id in judgments else item.comparison
        )
    for item in unresolved:
        item.comparison = judgments.get(item.attempt.assessment.candidate_id, "unassessed")
    unresolved_improvements = {
        item.attempt.assessment.candidate_id for item in unresolved if item.comparison == "improves"
    }
    if ranking.preferred_id in unresolved_improvements:
        decision.monotonicity = "unverified"
    elif ranking.preferred_id not in {candidate.candidate_id for candidate in top}:
        return decision

    decision.selected_id = ranking.preferred_id
    decision.decision = "qualitative"
    return decision
