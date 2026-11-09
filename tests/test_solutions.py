import asyncio

import pytest
from pydantic import BaseModel

from model_runtime import sum_usage
from schemas import GeneratedCase, GenerationInput, Requirement, UsageRecord
from solutions.ghl import TECHNIQUES, generate_ghl
from solutions.one_shot import generate_one_shot


class FakeRuntime:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []
        self.usage_records = []

    async def run(self, stage, instructions, input, output_type, *, extra=None):
        self.calls.append((stage, instructions, input, output_type, extra))
        answer, usage = next(self.responses)
        self.usage_records.append(usage)
        if isinstance(answer, dict):
            return output_type.model_validate(answer)
        return answer


class Selection(BaseModel):
    selections: list[dict[str, str]]


class CaseList(BaseModel):
    cases: list[GeneratedCase]


def make_input():
    return GenerationInput(
        unit_id="sample",
        requirements=[
            Requirement(id="R1", text="Save bookmark", language="en", source="fixture"),
            Requirement(id="R2", text="Restore bookmark", language="en", source="fixture"),
        ],
    )


def case(id, title, description, requirement_ids):
    return GeneratedCase(id=id, title=title, description=description, requirement_ids=requirement_ids)


def test_one_shot_makes_one_call_with_all_requirements_and_uses_stable_ids():
    fake = FakeRuntime([
        (CaseList(cases=[case("x", "Save", "Save one", ["R1"]), case("y", "Restore", "Restore one", ["R2"])]),
         UsageRecord(input_tokens=10, output_tokens=5))
    ])

    result = asyncio.run(generate_one_shot(make_input(), fake))

    assert len(fake.calls) == 1
    assert fake.calls[0][2].requirements == make_input().requirements
    assert [item.id for item in result.cases] == ["G-001", "G-002"]
    assert result.usage == UsageRecord(input_tokens=10, output_tokens=5)


def test_one_shot_rejects_unknown_requirement_ids():
    fake = FakeRuntime([(CaseList(cases=[case("x", "Save", "Save one", ["R999"])]), UsageRecord())])
    with pytest.raises(ValueError, match="R999"):
        asyncio.run(generate_one_shot(make_input(), fake))


def test_ghl_selects_techniques_then_calls_once_per_technique_with_full_input():
    names = [TECHNIQUES[0].id, TECHNIQUES[1].id]
    fake = FakeRuntime([
        ({"selections": [{"technique_id": names[0], "rationale": "Values matter"}, {"technique_id": names[1], "rationale": "Limits matter"}]}, UsageRecord(input_tokens=2, output_tokens=2)),
        (CaseList(cases=[case("same", "Boundary", "At lower limit", ["R1"])]), UsageRecord(input_tokens=3, output_tokens=4)),
        (CaseList(cases=[case("same", "Boundary", "At lower limit", ["R2"])]), UsageRecord(input_tokens=5, output_tokens=6)),
    ])

    result = asyncio.run(generate_ghl(make_input(), fake))

    assert len(fake.calls) == 3
    assert all(call[2].requirements == make_input().requirements for call in fake.calls)
    assert len(result.cases) == 1
    assert result.cases[0].id == "G-001"
    assert result.cases[0].requirement_ids == ["R1", "R2"]
    assert result.usage == sum_usage(fake.usage_records)
    assert result.selected_techniques == names
    assert [call[4]["output_mode"] for call in fake.calls[1:]] == ["batch", "batch"]


@pytest.mark.parametrize("output_mode", ["per_requirement", "per_case"])
def test_ghl_scoped_mode_calls_per_requirement_with_full_input(output_mode):
    requirement_ids = [requirement.id for requirement in make_input().requirements]
    fake = FakeRuntime([
        ({"selections": [{"technique_id": TECHNIQUES[0].id, "rationale": "Partition behavior"}]}, UsageRecord()),
        (CaseList(cases=[case("x-R1", "Target 1", "For R1", ["R1", "R2"])]), UsageRecord()),
        (CaseList(cases=[case("x-R2", "Target 2", "For R2", ["R2"])]), UsageRecord()),
    ])

    result = asyncio.run(generate_ghl(make_input(), fake, output_mode=output_mode))

    calls = fake.calls[1:]
    assert len(calls) == len(requirement_ids)
    assert all(call[2].requirements == make_input().requirements for call in calls)
    assert [call[4]["target"] for call in calls] == requirement_ids
    assert [call[4]["output_mode"] for call in calls] == [output_mode] * len(requirement_ids)
    assert len(result.cases) == len(requirement_ids)
    assert result.cases[0].requirement_ids == ["R1", "R2"]


def test_ghl_per_case_rejects_more_than_one_case_from_a_call():
    fake = FakeRuntime([
        ({"selections": [{"technique_id": TECHNIQUES[0].id, "rationale": "Partition behavior"}]}, UsageRecord()),
        (CaseList(cases=[case("a", "A", "a", ["R1"]), case("b", "B", "b", ["R1"])]), UsageRecord()),
    ])
    with pytest.raises(ValueError, match="more than one"):
        asyncio.run(generate_ghl(make_input(), fake, output_mode="per_case"))


def test_ghl_rejects_cases_without_the_scoped_requirement_link():
    fake = FakeRuntime([
        ({"selections": [{"technique_id": TECHNIQUES[0].id, "rationale": "Partition behavior"}]}, UsageRecord()),
        (CaseList(cases=[case("x", "Target", "For R2", ["R2"])]), UsageRecord()),
    ])
    with pytest.raises(ValueError, match="R1"):
        asyncio.run(generate_ghl(make_input(), fake, output_mode="per_requirement"))


def test_ghl_rejects_unknown_requirement_links():
    fake = FakeRuntime([
        ({"selections": [{"technique_id": TECHNIQUES[0].id, "rationale": "Partition behavior"}]}, UsageRecord()),
        (CaseList(cases=[case("x", "Target", "Invalid link", ["R1", "R999"])]), UsageRecord()),
    ])
    with pytest.raises(ValueError, match="R999"):
        asyncio.run(generate_ghl(make_input(), fake))


def test_ghl_rejects_invalid_selected_technique_and_duplicate_selection():
    fake = FakeRuntime([
        ({"selections": [{"technique_id": "unknown", "rationale": "fixture"}]}, UsageRecord()),
    ])
    with pytest.raises(ValueError, match="unknown"):
        asyncio.run(generate_ghl(make_input(), fake))
    fake = FakeRuntime([
        ({"selections": [{"technique_id": TECHNIQUES[0].id, "rationale": "a"}, {"technique_id": TECHNIQUES[0].id, "rationale": "b"}]}, UsageRecord()),
    ])
    with pytest.raises(ValueError, match="duplicate"):
        asyncio.run(generate_ghl(make_input(), fake))
