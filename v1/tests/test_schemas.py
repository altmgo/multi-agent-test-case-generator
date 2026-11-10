import json

import pytest
from pydantic import ValidationError

from schemas import (
    AgentOpinion,
    CandidateAssessment,
    EvaluationResult,
    GeneratedCase,
    GenerationInput,
    GenerationResult,
    HumanDecision,
    HumanEvaluation,
    ReferenceCase,
    Requirement,
    SemanticMatch,
    Unit,
    UsageRecord,
    generation_input,
    validate_cases,
)


@pytest.fixture
def unit() -> Unit:
    return Unit(
        id="firefox_bookmarks",
        requirements=[
            Requirement(
                id="R-001",
                text="  Salvar endereço\r\nsem alterar a URL.  ",
                language="pt",
                source="R-set.csv#R-001",
            ),
            Requirement(
                id="R-002",
                text="Abrir endereço salvo.",
                language="pt",
                source="R-set.csv#R-002",
            ),
        ],
        reference_cases=[
            ReferenceCase(
                id="TC-001",
                title="  Gabarito reservado  ",
                description="Passo 1\n\nPasso 2 ",
                requirement_ids=["R-001", "R-002"],
                source="T-set.csv#TC-001",
                link_method="inferred_row_alignment",
                link_status="pending_provenance_review",
                secondary_domains=["history"],
            )
        ],
        parent_id="firefox_legacy",
    )


@pytest.mark.parametrize("ids", [[], [""], [" \t "]])
def test_generated_case_requires_nonblank_requirement_ids(ids):
    with pytest.raises(ValidationError, match="requirement_ids"):
        GeneratedCase(id="G-001", title="T", description="D", requirement_ids=ids)


def test_validate_cases_rejects_unknown_requirement_id(unit):
    case = GeneratedCase(
        id="G-001",
        title="Abrir favorito",
        description="Abrir uma URL previamente salva.",
        requirement_ids=["R-001", "R-099"],
    )

    with pytest.raises(ValueError, match="R-099"):
        validate_cases(generation_input(unit), [case])


def test_multiple_valid_links_stay_on_one_case(unit):
    result = GenerationResult(
        cases=[
            GeneratedCase(
                id="G-001",
                title="Salvar e abrir favorito",
                description="Salvar URL e abrir pelo menu.",
                requirement_ids=["R-001", "R-002"],
            )
        ],
    )

    validate_cases(generation_input(unit), result.cases)
    assert len(result.cases) == 1
    assert result.cases[0].requirement_ids == ["R-001", "R-002"]


def test_generation_input_serializes_requirements_without_reference_data(unit):
    payload = json.loads(generation_input(unit).model_dump_json())

    assert payload["unit_id"] == "firefox_bookmarks"
    assert [requirement["id"] for requirement in payload["requirements"]] == [
        "R-001",
        "R-002",
    ]
    assert "reference_cases" not in payload
    assert "Gabarito reservado" not in str(payload)


def test_generation_input_rejects_reference_data(unit):
    with pytest.raises(ValidationError, match="reference_cases"):
        GenerationInput(
            unit_id=unit.id,
            requirements=unit.requirements,
            reference_cases=unit.reference_cases,
        )


def test_archived_parent_cannot_be_used_for_generation(unit):
    parent = Unit(
        id="firefox_legacy",
        requirements=unit.requirements,
        reference_cases=unit.reference_cases,
        generatable=False,
    )

    assert len(parent.reference_cases) == 1
    with pytest.raises(ValueError, match="firefox_legacy"):
        generation_input(parent)


def test_unit_with_no_reference_cases_can_be_used_for_generation(unit):
    without_references = Unit(id="e2edev", requirements=unit.requirements)

    assert without_references.reference_cases == []
    assert generation_input(without_references).unit_id == "e2edev"


def test_unit_round_trips_text_and_reference_provenance(unit):
    decoded = Unit.model_validate_json(unit.model_dump_json())
    reference = decoded.reference_cases[0]

    assert decoded.requirements[0].text == "  Salvar endereço\r\nsem alterar a URL.  "
    assert reference.title == "  Gabarito reservado  "
    assert reference.description == "Passo 1\n\nPasso 2 "
    assert reference.requirement_ids == ["R-001", "R-002"]
    assert reference.link_method == "inferred_row_alignment"
    assert reference.link_status == "pending_provenance_review"
    assert reference.source == "T-set.csv#TC-001"
    assert reference.secondary_domains == ["history"]
    assert decoded.parent_id == "firefox_legacy"


def test_usage_distinguishes_missing_counters_from_reported_zero():
    missing = UsageRecord()
    partial = UsageRecord(input_tokens=0, details={"cached_tokens": 0})
    available = UsageRecord(input_tokens=0, output_tokens=0)

    assert missing.status == "unavailable"
    assert missing.input_tokens is None
    assert missing.output_tokens is None
    assert partial.status == "partial"
    assert partial.input_tokens == 0
    assert partial.output_tokens is None
    assert partial.details == {"cached_tokens": 0}
    assert available.status == "available"
    assert UsageRecord.model_validate_json(partial.model_dump_json()) == partial


def test_evaluation_without_reference_cases_keeps_metrics_empty():
    result = EvaluationResult(status="not_evaluable", generated_count=2)

    assert result.reference_count == 0
    assert result.matches == []
    assert result.precision is None
    assert result.recall is None
    assert result.f1 is None


def test_assessment_keeps_candidate_and_agent_feedback():
    assessment = CandidateAssessment(
        candidate_id="attempt-1",
        cases=[
            GeneratedCase(id="G-001", title="T", description="D", requirement_ids=["R-001"])
        ],
        opinions=[
            AgentOpinion(agent="critic", feedback="Missing edge case.", request_revision=True)
        ],
        confirmed_blockers=1,
    )

    decoded = CandidateAssessment.model_validate_json(assessment.model_dump_json())
    assert decoded.cases[0].id == "G-001"
    assert decoded.opinions[0].feedback == "Missing edge case."
    assert decoded.opinions[0].request_revision is True
    assert decoded.confirmed_blockers == 1


def test_evaluation_round_trips_raw_similarity_and_unmatched_ids():
    result = EvaluationResult(
        status="evaluated",
        generated_count=2,
        reference_count=2,
        precision=0.5,
        recall=0.5,
        f1=0.5,
        matches=[
            SemanticMatch(
                generated_id="G-001",
                reference_id="TC-001",
                similarity=0.700001,
            )
        ],
        unmatched_generated_ids=["G-002"],
        unmatched_reference_ids=["TC-002"],
    )

    decoded = EvaluationResult.model_validate_json(result.model_dump_json())
    assert decoded.matches[0].similarity == 0.700001
    assert decoded.unmatched_generated_ids == ["G-002"]
    assert decoded.unmatched_reference_ids == ["TC-002"]


def test_human_evaluation_keeps_inconclusive_decision_and_justification():
    result = HumanEvaluation(
        generated_count=3,
        reference_count=2,
        decisions=[
            HumanDecision(
                generated_id="G-001",
                reference_id="TC-001",
                verdict="inconclusive",
                justification="The setup is underspecified.",
            )
        ],
        inconclusive_count=1,
    )

    decoded = HumanEvaluation.model_validate_json(result.model_dump_json())
    assert decoded.scope == "automatic_matches_only"
    assert decoded.decisions[0].verdict == "inconclusive"
    assert decoded.decisions[0].justification == "The setup is underspecified."
    assert decoded.inconclusive_count == 1
