import json

import pytest

from datasets.profile import (
    calibration_profile,
    coverage_profile,
    save_calibration_profile,
    save_coverage_profile,
)
from schemas import ReferenceCase, Requirement, Unit


def make_unit(unit_id, requirements, cases=()):
    return Unit(
        id=unit_id,
        requirements=[
            Requirement(id=identifier, text="Requirement", language="en", source="fixture")
            for identifier in requirements
        ],
        reference_cases=[
            ReferenceCase(
                id=f"case-{index}",
                title="Scenario",
                description="Given a precondition",
                requirement_ids=list(links),
                source="fixture",
                link_method="explicit",
                link_status="verified",
            )
            for index, links in enumerate(cases)
        ],
    )


def test_coverage_counts_each_scenario_once_per_linked_requirement():
    unit = make_unit("sample", ["R3", "R1", "R2"], [("R3", "R2", "R3"), ("R3",)])

    assert coverage_profile([unit]) == {
        "table": [
            {"unit_id": "sample", "requirement_id": "R1", "scenario_count": 0},
            {"unit_id": "sample", "requirement_id": "R2", "scenario_count": 1},
            {"unit_id": "sample", "requirement_id": "R3", "scenario_count": 2},
        ],
        "aggregate": {
            "requirement_count": 3,
            "histogram": {"0": 1, "1": 1, "2": 1},
            "quartiles": {"q1": 0.5, "median": 1.0, "q3": 1.5},
        },
    }


def test_coverage_of_empty_corpus_has_undefined_quartiles():
    assert coverage_profile([make_unit("empty", [])]) == {
        "table": [],
        "aggregate": {
            "requirement_count": 0,
            "histogram": {},
            "quartiles": {"q1": None, "median": None, "q3": None},
        },
    }


def test_calibration_contains_only_aggregate_from_explicit_sample():
    sample = make_unit("sample", ["R1", "R2"], [("R2",)])
    target = make_unit("target", ["R1"], [("R1",), ("R1",)])
    ignored = make_unit("ignored", ["R1"])

    assert calibration_profile([target, ignored, sample], {"sample"}, {"target"}) == {
        "requirement_count": 2,
        "histogram": {"0": 1, "1": 1},
        "quartiles": {"q1": 0.25, "median": 0.5, "q3": 0.75},
    }


@pytest.mark.parametrize(
    ("calibration_ids", "evaluated_ids", "error"),
    [
        ({"sample"}, {"sample"}, "overlap.*sample"),
        ({"missing"}, {"sample"}, "Unknown calibration unit IDs.*missing"),
        ({"sample"}, {"missing"}, "Unknown evaluated unit IDs.*missing"),
        (set(), {"sample"}, "at least one calibration unit"),
        ({"empty"}, {"sample"}, "at least one requirement"),
    ],
)
def test_calibration_rejects_invalid_selection(calibration_ids, evaluated_ids, error):
    units = [make_unit("sample", ["R1"]), make_unit("empty", [])]
    with pytest.raises(ValueError, match=error):
        calibration_profile(units, calibration_ids, evaluated_ids)


def test_calibration_rejects_ambiguous_unit_ids():
    units = [make_unit("sample", ["R1"]), make_unit("sample", ["R2"])]
    with pytest.raises(ValueError, match="Duplicate unit ID.*sample"):
        calibration_profile(units, {"sample"}, set())


def test_save_coverage_profile_writes_sorted_table_and_versioned_provenance(tmp_path):
    units = [make_unit("z-unit", ["R1"], [("R1",)]), make_unit("a-unit", ["R1"])]
    output = tmp_path / "e2edev_coverage.json"

    save_coverage_profile(units, output, dataset_version="dataset-sha")
    save_coverage_profile(list(reversed(units)), output, dataset_version="dataset-sha")

    assert output.with_suffix(".csv").read_bytes() == (
        b"unit_id,requirement_id,scenario_count\na-unit,R1,0\nz-unit,R1,1\n"
    )
    assert output.with_suffix(".histogram.csv").read_bytes() == (
        b"scenario_count,requirement_count\n0,1\n1,1\n"
    )
    assert json.loads(output.read_text()) == {
        "profile_version": 1,
        "dataset_version": "dataset-sha",
        "scope": "descriptive",
        "unit_ids": ["a-unit", "z-unit"],
        "aggregate": {
            "requirement_count": 2,
            "histogram": {"0": 1, "1": 1},
            "quartiles": {"q1": 0.25, "median": 0.5, "q3": 0.75},
        },
    }


def test_save_calibration_keeps_provenance_separate_from_model_payload(tmp_path):
    units = [make_unit("sample", ["R1"]), make_unit("target", ["R1"])]

    output = tmp_path / "calibration.json"
    save_calibration_profile(
        units, {"sample"}, {"target"}, output, dataset_version="dataset-sha"
    )

    assert {path.name for path in tmp_path.iterdir()} == {
        "calibration.json", "calibration.provenance.json"
    }
    assert json.loads(output.read_text()) == {
        "requirement_count": 1,
        "histogram": {"0": 1},
        "quartiles": {"q1": 0.0, "median": 0.0, "q3": 0.0},
    }
    assert json.loads(output.with_suffix(".provenance.json").read_text()) == {
        "profile_version": 1,
        "dataset_version": "dataset-sha",
        "scope": "calibration",
        "unit_ids": ["sample"],
        "evaluated_unit_ids": ["target"],
    }


def test_save_coverage_rejects_output_that_would_replace_its_table(tmp_path):
    output = tmp_path / "coverage.csv"

    with pytest.raises(ValueError, match=r"\bJSON\b"):
        save_coverage_profile([], output, dataset_version="dataset-sha")

    assert list(tmp_path.iterdir()) == []
