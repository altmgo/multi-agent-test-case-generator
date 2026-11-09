import asyncio
from copy import deepcopy

import pytest
from pydantic import ValidationError

from schemas import AgentOpinion, CandidateAssessment, GenerationInput, Requirement, UsageRecord
from solutions.multiagent import MultiagentFailure
from solutions.multiagent.coverage import E2EDevCalibrationProfile
from solutions.multiagent.orchestrator import run_multiagent
from solutions.multiagent.selection import select_candidate


INPUT = GenerationInput(
    unit_id="bookmarks",
    requirements=[
        Requirement(id="R1", text="Save a bookmark", language="en", source="fixture"),
        Requirement(id="R2", text="Restore a bookmark", language="en", source="fixture"),
    ],
)


def case(title, requirement="R1", description=None):
    return {
        "id": "model-id",
        "title": title,
        "description": description or title,
        "requirement_ids": [requirement],
    }


def opinion(feedback="Clear", *, request=False, blockers=(), complete=True):
    return {
        "feedback": feedback,
        "request_revision": request,
        "confirmed_blockers": list(blockers),
        "blocker_assessment_complete": complete,
    }


class ScriptedRuntime:
    """Replace only the structured model boundary and its usage counter."""

    def __init__(self, script):
        self.remaining = iter(script)
        self.calls = []
        self.usage_records = [UsageRecord(input_tokens=999, output_tokens=999)]

    async def run(self, stage, instructions, input, output_type, *, extra=None):
        assert input == INPUT
        expected_stage, response = next(self.remaining)
        assert stage == f"multiagent_{expected_stage}"
        assert instructions
        assert extra["prompt_version"] == "multiagent-v1"
        self.calls.append((expected_stage, deepcopy(extra)))
        self.usage_records.append(UsageRecord(input_tokens=2, output_tokens=1))
        if isinstance(response, Exception):
            raise response
        return output_type.model_validate(response)

    def finish(self):
        assert next(self.remaining, None) is None


def run(script, enabled, rounds=1, **kwargs):
    runtime = ScriptedRuntime(script)
    result = asyncio.run(run_multiagent(INPUT, runtime, enabled, rounds, **kwargs))
    runtime.finish()
    assert result.usage == UsageRecord(
        input_tokens=2 * len(runtime.calls), output_tokens=len(runtime.calls)
    )
    assert result.trace["status"] == "completed"
    assert result.trace["pending_controls"] == []
    assert result.model_validate_json(result.model_dump_json()) == result
    return result, runtime.calls


def test_critic_round_replays_analyst_and_critic_on_three_independent_candidates():
    result, calls = run(
        [
            ("analyst", {"analysis": "Initial analysis"}),
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion("Fix blocker", request=True, blockers=["Unsupported expected result"])),
            ("analyst", {"analysis": "First analysis"}),
            ("generator", {"cases": [case("First")]}),
            ("critic", opinion("First still blocked", request=True, blockers=["Same blocker"])),
            ("analyst", {"analysis": "Second analysis"}),
            ("generator", {"cases": [case("Second"), case("Restore", "R2")]}),
            ("critic", opinion()),
            ("analyst", {"analysis": "Third analysis"}),
            ("generator", {"cases": [case("Third")]}),
            ("critic", opinion()),
            ("validator", opinion()),
        ],
        {"analyst", "critic", "validator"},
        rounds=2,
    )

    analysts = [extra for stage, extra in calls if stage == "analyst"][1:]
    generators = [extra for stage, extra in calls if stage == "generator"][1:]
    assert len(analysts) == len(generators) == 3
    for analyst, generator, analysis in zip(
        analysts, generators, ("First analysis", "Second analysis", "Third analysis"), strict=True
    ):
        assert analyst["revision"] == generator["revision"] == analysts[0]["revision"]
        assert generator["analysis"]["analysis"] == analysis
    revision = analysts[0]["revision"]
    assert revision["accepted_id"] == "initial"
    assert revision["cases"][0]["title"] == "Initial"
    assert revision["feedback"][-1]["feedback"] == "Fix blocker"

    assert [(item.id, item.title) for item in result.cases] == [("G-001", "Second"), ("G-002", "Restore")]
    trace = result.trace
    assert trace["initial"]["assessment"]["cases"][0]["title"] == "Initial"
    assert trace["initial"]["analysis"]["analysis"] == "Initial analysis"
    revision_round, = trace["rounds"]
    assert revision_round["requester"] == "critic"
    assert [item["comparison"] for item in revision_round["candidates"]] == ["ties", "improves", "improves"]
    assert revision_round["monotonicity"] == "confirmed"
    assert len(trace["calls"]) == len(calls)
    assert all(call["usage"][0]["input_tokens"] == 2 for call in trace["calls"])
    assert trace["pending"] == []


def test_validator_round_replays_critic_and_validator_without_nested_critic_rounds():
    result, calls = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion()),
            ("validator", opinion("Fix unsupported result", request=True, blockers=["Unsupported result"])),
            ("generator", {"cases": [case("First"), case("Restore", "R2")]}),
            ("critic", opinion("Please revise this case", request=True)),
            ("validator", opinion()),
            ("generator", {"cases": [case("Second")]}),
            ("critic", opinion("Blocked", request=True, blockers=["Blocked"])),
            ("validator", opinion()),
            ("generator", {"cases": [case("Third")]}),
            ("critic", opinion("Still blocked", blockers=["Blocked"])),
            ("validator", opinion()),
        ],
        {"critic", "validator"},
        rounds=3,
    )

    revision_round, = result.trace["rounds"]
    assert revision_round["requester"] == "validator"
    assert [item["comparison"] for item in revision_round["candidates"]] == ["improves", "ties", "ties"]
    assert result.cases[0].title == "First"
    assert [(item["agent"], item["reason"]) for item in result.trace["pending"]] == [
        ("critic", "checkpoint_passed")
    ]
    assert all(extra["revision"]["accepted_id"] == "initial" for stage, extra in calls[3:] if stage == "generator")


def test_tied_critic_round_does_not_consume_validator_opportunity():
    result, _ = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion("Critic asks", request=True)),
            *[(stage, value) for title in ("A", "B", "C") for stage, value in (
                ("generator", {"cases": [case(title)]}), ("critic", opinion())
            )],
            ("validator", opinion("Validator asks", request=True)),
            *[(stage, value) for title in ("D", "E", "F") for stage, value in (
                ("generator", {"cases": [case(title)]}), ("critic", opinion()), ("validator", opinion())
            )],
        ],
        {"critic", "validator"},
        rounds=2,
    )

    assert result.cases[0].title == "Initial"
    assert [round["requester"] for round in result.trace["rounds"]] == ["critic", "validator"]
    assert all(round["selected_id"] == "initial" for round in result.trace["rounds"])
    assert all(
        item["comparison"] == "ties"
        for round in result.trace["rounds"]
        for item in round["candidates"]
    )
    assert {item["agent"] for item in result.trace["pending"]} == {"critic", "validator"}


def test_all_invalid_revisions_preserve_accepted_and_audit_provider_attempts():
    result, _ = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("validator", opinion("Find boundaries", request=True)),
            ("generator", {"cases": [case("Invalid link", "unknown")]}),
            ("generator", ValueError("Malformed revision")),
            ("generator", {"cases": [case("Another invalid link", "unknown")]}),
        ],
        {"validator"},
    )

    assert result.cases[0].title == "Initial"
    revision_round, = result.trace["rounds"]
    assert [item["comparison"] for item in revision_round["candidates"]] == ["invalid"] * 3
    assert all(not item["attempt"]["assessment"]["valid"] for item in revision_round["candidates"])
    assert any(call["error_type"] == "ValueError" for call in result.trace["calls"])
    assert result.trace["pending"][0]["agent"] == "validator"
    assert result.trace["pending"][0]["reason"] == "round_limit"


def test_zero_rounds_leaves_both_requests_pending_without_replaying_controls():
    result, _ = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion("Critic asks", request=True)),
            ("validator", opinion("Validator asks", request=True)),
        ],
        {"critic", "validator"},
        rounds=0,
    )

    assert result.trace["rounds"] == []
    assert [(item["agent"], item["reason"]) for item in result.trace["pending"]] == [
        ("critic", "round_limit"), ("validator", "round_limit")
    ]


def test_coverage_receives_generated_case_index_and_only_typed_aggregate():
    profile = E2EDevCalibrationProfile.model_validate(
        {"requirement_count": 2, "histogram": {"0": 1, "2": 1}, "quartiles": {"q1": 0.5, "median": 1, "q3": 1.5}}
    )
    with pytest.raises(ValidationError):
        E2EDevCalibrationProfile.model_validate({**profile.model_dump(), "evaluated_unit_ids": ["secret"]})
    with pytest.raises(ValidationError):
        E2EDevCalibrationProfile.model_validate({**profile.model_dump(), "histogram": {"R1": 1}})
    result, calls = run(
        [
            ("generator", {"cases": [case("Accepted")]}),
            ("critic", opinion(request=True)),
            *[(stage, value) for title in ("A", "B", "C") for stage, value in (
                ("generator", {"cases": [case(title)]}), ("critic", opinion())
            )],
            ("coverage", {"feedback": "Consider an R2 scenario."}),
        ],
        {"critic", "coverage"},
        calibration_profile=profile,
    )

    coverage, extra = calls[-1]
    assert coverage == "coverage"
    assert extra["calibration_profile"] == profile.model_dump(mode="json")
    assert all("calibration_profile" not in extra for _, extra in calls[:-1])
    assert [item["title"] for item in extra["case_index"]["accepted"]] == ["Accepted"]
    assert [item["title"] for item in extra["case_index"]["rejected"]] == ["A", "B", "C"]
    assert result.trace["coverage"]["feedback"] == "Consider an R2 scenario."
    assert result.cases[0].title == "Accepted"


def test_qualitative_rank_can_choose_tied_better_candidates_but_never_worse():
    result, calls = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("validator", opinion(request=True)),
            ("generator", {"cases": [case("Better A"), case("Restore", "R2")]}),
            ("validator", opinion()),
            ("generator", {"cases": [case("Better B"), case("Restore", "R2")]}),
            ("validator", opinion()),
            ("generator", {"cases": [case("Worse"), case("Worse")]}),
            ("validator", opinion()),
            ("selection", {"preferred_id": "round-1-candidate-3", "rationale": "Prefer the ineligible case.", "judgments": []}),
        ],
        {"validator"},
    )

    extra = calls[-1][1]
    assert [item["candidate_id"] for item in extra["candidates"]] == [
        "round-1-candidate-1", "round-1-candidate-2"
    ]
    assert result.cases[0].title == "Better A"
    revision_round, = result.trace["rounds"]
    assert [item["comparison"] for item in revision_round["candidates"]] == ["improves", "improves", "worse"]
    assert revision_round["decision"] == "objective"
    assert revision_round["monotonicity"] == "confirmed"


def test_qualitative_improvement_with_incomplete_blocker_evidence_is_unverified():
    result, _ = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion(request=True)),
            ("generator", {"cases": [case("Possible improvement")]}),
            ("critic", opinion(complete=False)),
            ("generator", {"cases": [case("Objective tie")]}),
            ("critic", opinion()),
            ("generator", {"cases": [case("Objective loss"), case("Objective loss")]}),
            ("critic", opinion()),
            ("selection", {
                "preferred_id": "round-1-candidate-1",
                "rationale": "Grounded scenario is more actionable.",
                "judgments": [{"candidate_id": "round-1-candidate-1", "comparison": "improves"}],
            }),
        ],
        {"critic"},
    )

    assert result.cases[0].title == "Possible improvement"
    revision_round, = result.trace["rounds"]
    assert [item["comparison"] for item in revision_round["candidates"]] == ["improves", "ties", "worse"]
    assert revision_round["decision"] == "qualitative"
    assert revision_round["monotonicity"] == result.trace["monotonicity"] == "unverified"


def test_selection_uses_blockers_coverage_then_duplicates_and_keeps_exact_ties():
    accepted = CandidateAssessment(candidate_id="accepted", cases=[], confirmed_blockers=1, covered_requirements=2, duplicates=1)
    higher_coverage = accepted.model_copy(update={"candidate_id": "coverage", "covered_requirements": 3})
    fewer_blockers = accepted.model_copy(update={"candidate_id": "blockers", "confirmed_blockers": 0, "covered_requirements": 0})
    fewer_duplicates = accepted.model_copy(update={"candidate_id": "duplicates", "duplicates": 0})
    invalid = fewer_blockers.model_copy(update={"candidate_id": "invalid", "valid": False})
    tie = accepted.model_copy(update={"candidate_id": "tie"})

    assert select_candidate(accepted, [tie, invalid]) is accepted
    assert select_candidate(accepted, [fewer_duplicates, tie]) is fewer_duplicates
    assert select_candidate(accepted, [fewer_duplicates, higher_coverage]) is higher_coverage
    assert select_candidate(accepted, [higher_coverage, fewer_blockers]) is fewer_blockers


@pytest.mark.parametrize("output_mode", ["per_requirement", "per_case"])
def test_scoped_generation_receives_complete_input_and_skips_disabled_agents(output_mode):
    result, calls = run(
        [
            ("generator", {"cases": [case("Save")]}),
            ("generator", {"cases": [case("Restore", "R2")]}),
        ],
        set(),
        output_mode=output_mode,
    )

    assert [item["target"] for _, item in calls] == ["R1", "R2"]
    assert [item["output_mode"] for _, item in calls] == [output_mode, output_mode]
    assert result.trace["rounds"] == []
    assert [item.id for item in result.cases] == ["G-001", "G-002"]


def test_round_candidate_opinions_and_scores_remain_as_used_in_the_decision():
    result, _ = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion("Initial blocker", request=True, blockers=["Unclear setup"])),
            ("generator", {"cases": [case("First")]}),
            ("critic", opinion()),
            ("generator", {"cases": [case("Second")]}),
            ("critic", opinion(blockers=["Unclear setup"])),
            ("generator", {"cases": [case("Third")]}),
            ("critic", opinion(blockers=["Unclear setup"])),
            ("validator", opinion("Later blocker", request=True, blockers=["Unsupported behavior"])),
        ],
        {"critic", "validator"},
    )

    revision_round, = result.trace["rounds"]
    assessed = revision_round["candidates"][0]["attempt"]["assessment"]
    assert [item["agent"] for item in assessed["opinions"]] == ["critic"]
    assert assessed["confirmed_blockers"] == 0
    assert result.trace["accepted_assessment"]["confirmed_blockers"] == 1
    assert result.trace["pending"][0]["opinion"]["confirmed_blockers"] == ["Unsupported behavior"]


def test_qualitative_rank_can_promote_the_second_of_two_tied_improvements():
    result, _ = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("validator", opinion(request=True)),
            ("generator", {"cases": [case("Better A"), case("Restore", "R2")]}),
            ("validator", opinion()),
            ("generator", {"cases": [case("Better B"), case("Restore", "R2")]}),
            ("validator", opinion()),
            ("generator", {"cases": [case("Tie")]}),
            ("validator", opinion()),
            ("selection", {"preferred_id": "round-1-candidate-2", "rationale": "Sharper expectations.", "judgments": []}),
        ],
        {"validator"},
    )

    assert result.cases[0].title == "Better B"
    revision_round, = result.trace["rounds"]
    assert revision_round["decision"] == "qualitative"
    assert revision_round["monotonicity"] == "confirmed"


def test_revision_can_retry_from_the_new_accepted_state_until_shared_limit():
    result, calls = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion(request=True, blockers=["Bad setup", "Wrong expected result"])),
            ("generator", {"cases": [case("Partial")]}),
            ("critic", opinion("Correct the result", request=True, blockers=["Wrong expected result"])),
            ("generator", {"cases": [case("Tie 1")]}),
            ("critic", opinion(blockers=["Bad setup", "Wrong expected result"])),
            ("generator", {"cases": [case("Tie 2")]}),
            ("critic", opinion(blockers=["Bad setup", "Wrong expected result"])),
            ("generator", {"cases": [case("Complete")]}),
            ("critic", opinion()),
            ("generator", {"cases": [case("Tie 3")]}),
            ("critic", opinion(blockers=["Wrong expected result"])),
            ("generator", {"cases": [case("Tie 4")]}),
            ("critic", opinion(blockers=["Wrong expected result"])),
            ("validator", opinion("Check a boundary", request=True)),
        ],
        {"critic", "validator"},
        rounds=2,
    )

    assert [item["requester"] for item in result.trace["rounds"]] == ["critic", "critic"]
    revisions = [extra["revision"] for stage, extra in calls if stage == "generator"][4:]
    assert all(item["accepted_id"] == "round-1-candidate-1" for item in revisions)
    assert all(item["feedback"][0]["feedback"] == "Correct the result" for item in revisions)
    assert result.cases[0].title == "Complete"
    assert [(item["agent"], item["reason"]) for item in result.trace["pending"]] == [
        ("validator", "round_limit")
    ]


@pytest.mark.parametrize(
    "blockers, cases",
    [
        (["Unclear setup"], [case("More coverage"), case("Restore", "R2")]),
        ([], [case("Duplicate"), case("Duplicate")]),
    ],
)
def test_incomplete_review_cannot_override_a_provable_regression(blockers, cases):
    result, calls = run(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("validator", opinion(request=True)),
            ("generator", {"cases": cases}),
            ("validator", opinion(blockers=blockers, complete=False)),
            ("generator", {"cases": [case("Better A"), case("Restore", "R2")]}),
            ("validator", opinion()),
            ("generator", {"cases": [case("Better B"), case("Restore", "R2")]}),
            ("validator", opinion()),
            ("selection", {
                "preferred_id": "round-1-candidate-1",
                "rationale": "Prefer the incomplete assessment.",
                "judgments": [{"candidate_id": "round-1-candidate-1", "comparison": "improves"}],
            }),
        ],
        {"validator"},
    )

    assert [item["candidate_id"] for item in calls[-1][1]["candidates"]] == [
        "round-1-candidate-2", "round-1-candidate-3"
    ]
    assert result.cases[0].title == "Better A"
    revision_round, = result.trace["rounds"]
    assert revision_round["candidates"][0]["comparison"] == "worse"


def test_public_selection_ignores_assessments_from_a_different_control_prefix():
    critic = AgentOpinion(agent="critic", feedback="Reviewed")
    validator = AgentOpinion(agent="validator", feedback="Reviewed", confirmed_blockers=["Wrong result"])
    baseline = CandidateAssessment(
        candidate_id="accepted", cases=[], confirmed_blockers=1, opinions=[critic, validator]
    )
    critic_only = baseline.model_copy(update={
        "candidate_id": "critic-only", "confirmed_blockers": 0, "opinions": [critic]
    })
    reverse_order = critic_only.model_copy(update={
        "candidate_id": "reverse-order", "opinions": [validator, critic]
    })

    assert select_candidate(baseline, [critic_only, reverse_order]) is baseline


def test_complete_candidate_can_improve_on_lower_bound_of_incomplete_baseline():
    baseline = CandidateAssessment(
        candidate_id="accepted", cases=[], confirmed_blockers=1, comparable=False,
        opinions=[AgentOpinion(
            agent="validator", feedback="Uncertain", confirmed_blockers=["Wrong result"],
            blocker_assessment_complete=False,
        )],
    )
    candidate = CandidateAssessment(
        candidate_id="candidate", cases=[], confirmed_blockers=0,
        opinions=[AgentOpinion(agent="validator", feedback="Reviewed")],
    )

    assert select_candidate(baseline, [candidate]) is candidate


def test_validator_failure_exposes_completed_rounds_and_last_accepted_snapshot():
    runtime = ScriptedRuntime(
        [
            ("generator", {"cases": [case("Initial")]}),
            ("critic", opinion(request=True, blockers=["Unsupported result", "Bad setup"])),
            ("generator", {"cases": [case("Improvement")]}),
            ("critic", opinion("Improve setup", request=True, blockers=["Bad setup"])),
            ("generator", {"cases": [case("Tie 1")]}),
            ("critic", opinion(blockers=["Unsupported result", "Bad setup"])),
            ("generator", {"cases": [case("Tie 2")]}),
            ("critic", opinion(blockers=["Unsupported result", "Bad setup"])),
            ("validator", ValueError("raw provider payload")),
        ]
    )

    with pytest.raises(MultiagentFailure) as raised:
        asyncio.run(run_multiagent(INPUT, runtime, {"critic", "validator"}, 1))

    partial = raised.value.partial_result
    runtime.finish()
    assert "raw provider payload" not in str(raised.value)
    assert "raw provider payload" not in partial.model_dump_json()
    assert raised.value.__cause__ is raised.value.__context__ is None
    assert [item.title for item in partial.cases] == ["Improvement"]
    assert partial.usage == UsageRecord(input_tokens=18, output_tokens=9)
    trace = partial.trace
    assert trace["status"] == "failed"
    assert trace["failure"]["stage"] == "validator"
    assert trace["failure"]["error_type"] == "ValueError"
    assert trace["accepted_id"] == "round-1-candidate-1"
    assert trace["rounds"][0]["selected_id"] == trace["accepted_id"]
    assert trace["pending_controls"] == ["validator"]
    assert [(item["agent"], item["reason"]) for item in trace["pending"]] == [
        ("critic", "round_limit")
    ]
    assert trace["calls"][-1]["usage"][0]["input_tokens"] == 2
    assert partial.model_validate_json(partial.model_dump_json()) == partial


def test_initial_generation_failure_exposes_partial_outputs_without_accepted_cases():
    runtime = ScriptedRuntime(
        [
            ("analyst", {"analysis": "Initial analysis"}),
            ("generator", {"cases": [case("Save")]}),
            ("generator", ValueError("raw provider payload")),
        ]
    )

    with pytest.raises(MultiagentFailure) as raised:
        asyncio.run(run_multiagent(
            INPUT, runtime, {"analyst", "critic", "validator"}, 2, output_mode="per_requirement"
        ))

    partial = raised.value.partial_result
    runtime.finish()
    assert partial.cases == []
    assert partial.usage == UsageRecord(input_tokens=6, output_tokens=3)
    trace = partial.trace
    assert trace["status"] == "failed"
    assert trace["failure"]["stage"] == "generator"
    assert trace["initial"]["analysis"]["analysis"] == "Initial analysis"
    assert trace["initial"]["assessment"]["cases"][0]["title"] == "Save"
    assert trace["initial"]["assessment"]["valid"] is False
    assert trace["accepted_id"] is trace["accepted_assessment"] is None
    assert trace["pending_controls"] == ["critic", "validator"]
    assert "raw provider payload" not in partial.model_dump_json()
