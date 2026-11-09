import hashlib
import json
from pathlib import Path

import pytest

from datasets import e2edev
from datasets.e2edev import prepare_e2edev
from schemas import Unit

COMMIT = "d280dd144fbff30c237af26c1a76948e2f8857fa"
ANNOTATION = "requirment_with_tests.json"
GHERKIN = (
    "Feature: Busca por cidade\n"
    "  Encontra conteúdo em português.\n\n"
    "  Scenario: Exibir São Paulo\n"
    '    Given a query for "São Paulo"\n'
    "    Then the matching city appears\n"
)
SECOND_GHERKIN = "Feature: Busca\n  Scenario: Limpar a busca\n    Then the list resets"


def _annotation(source: Path, benchmark: str) -> Path:
    return source / "E2EDev_data" / f"E2ESD_Bench_{benchmark}" / ANNOTATION


def _write_annotation(path: Path, rows: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "summary": {
                    "overview": "SUMMARY_SENTINEL",
                    "predefined_options": [],
                    "external_resources": [],
                    "external_js_libraries": [],
                },
                "finegrained_rewith_test": rows,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _case(gherkin: str) -> dict:
    return {
        "test_case": [gherkin],
        "step_code": 'raise RuntimeError("PYTHON_SENTINEL")',
    }


def _manifest(output: Path) -> dict:
    return json.loads((output / "manifests/e2edev.json").read_bytes())


@pytest.fixture
def dataset(tmp_path, monkeypatch):
    source = tmp_path / "raw"
    output = tmp_path / "normalized"
    annotation = _annotation(source, "01")
    _write_annotation(
        annotation,
        {
            "3": {"requirement": {"description": "Sem cenário"}, "test_cases": []},
            "1": {
                "requirement": {"description": "Buscar São Paulo e exibir a região."},
                "test_cases": [_case(GHERKIN), _case(SECOND_GHERKIN)],
            },
        },
    )
    # The real source tree includes project code and a second annotation dataset.
    (annotation.parent / "source_code.py").write_text("SOURCE_CODE_SENTINEL", encoding="utf-8")
    alternate = source / "E2EDev_data_withTestID" / "E2ESD_Bench_01" / ANNOTATION
    _write_annotation(alternate, {})
    monkeypatch.setattr(
        e2edev, "ANNOTATION_SHA256", {"01": hashlib.sha256(annotation.read_bytes()).hexdigest()}
    )
    return source, output


def test_preserves_unicode_gherkin_links_and_original_positions(dataset):
    source, output = dataset
    (unit,) = prepare_e2edev(source, COMMIT, output)
    assert unit.id == "e2edev_bench_01"
    assert [req.id for req in unit.requirements] == ["e2edev_bench_01-R-1", "e2edev_bench_01-R-3"]
    first_requirement = unit.requirements[0]
    assert first_requirement.text == "Buscar São Paulo e exibir a região."
    annotation = "E2EDev_data/E2ESD_Bench_01/requirment_with_tests.json"
    assert first_requirement.source == f"{annotation}#/finegrained_rewith_test/1/requirement/description"
    assert [case.id for case in unit.reference_cases] == [
        "e2edev_bench_01-R-1-TC-1",
        "e2edev_bench_01-R-1-TC-2",
    ]
    first_case, second_case = unit.reference_cases
    assert first_case.title == "Exibir São Paulo"
    assert first_case.description == GHERKIN
    assert first_case.source == f"{annotation}#/finegrained_rewith_test/1/test_cases/0/test_case"
    assert second_case.description == SECOND_GHERKIN
    assert first_case.requirement_ids == second_case.requirement_ids == [first_requirement.id]
    assert unit.requirements[1].text == "Sem cenário"
    assert _manifest(output)["exclusions"] == []


def test_publishes_units_and_metadata_without_executing_or_serializing_python(dataset):
    source, output = dataset
    (unit,) = prepare_e2edev(source, COMMIT, output)
    unit_path = output / "e2edev_bench_01.json"
    manifest_path = output / "manifests/e2edev.json"
    assert Unit.model_validate_json(unit_path.read_bytes()) == unit
    for path in (unit_path, manifest_path):
        text = path.read_text(encoding="utf-8")
        assert "PYTHON_SENTINEL" not in text
        assert "SOURCE_CODE_SENTINEL" not in text
        assert "SUMMARY_SENTINEL" not in text
    assert "São Paulo" in unit_path.read_text(encoding="utf-8")
    assert "São Paulo" not in manifest_path.read_text(encoding="utf-8")
    manifest = _manifest(output)
    assert manifest["source"]["commit"] == COMMIT
    assert manifest["source"]["license"] is None
    assert manifest["raw_files"] == {
        "E2EDev_data/E2ESD_Bench_01/requirment_with_tests.json": {
            "sha256": hashlib.sha256(_annotation(source, "01").read_bytes()).hexdigest(),
        }
    }


def test_keeps_valid_records_and_reports_invalid_annotations(dataset):
    source, output = dataset
    bad_json = _annotation(source, "03")
    bad_json.parent.mkdir()
    bad_json.write_bytes(b"{ broken json")
    _write_annotation(
        _annotation(source, "04"),
        {
            "1": {"requirement": {"description": ""}, "test_cases": []},
            "2": {"requirement": {"description": "Missing cases"}},
            "3": {
                "requirement": {"description": "Malformed case followed by a valid one"},
                "test_cases": [_case("not Gherkin"), _case(GHERKIN)],
            },
            "4": {"requirement": {"description": "Invalid case list"}, "test_cases": "invalid"},
        },
    )
    e2edev.ANNOTATION_SHA256.update(
        {key: hashlib.sha256(_annotation(source, key).read_bytes()).hexdigest() for key in ("03", "04")}
    )
    units = prepare_e2edev(source, COMMIT, output)
    assert [unit.id for unit in units] == ["e2edev_bench_01", "e2edev_bench_04"]
    assert [req.id for req in units[1].requirements] == [
        "e2edev_bench_04-R-2",
        "e2edev_bench_04-R-3",
        "e2edev_bench_04-R-4",
    ]
    assert [case.id for case in units[1].reference_cases] == ["e2edev_bench_04-R-3-TC-2"]
    manifest = _manifest(output)
    assert {entry["reason"] for entry in manifest["exclusions"]} == {
        "invalid_annotation_json",
        "invalid_requirement_description",
        "missing_test_cases",
        "invalid_gherkin",
        "invalid_test_cases",
    }
    assert {
        entry["source"]
        for entry in manifest["exclusions"]
        if entry["reason"] == "invalid_gherkin"
    } == {"E2EDev_data/E2ESD_Bench_04/requirment_with_tests.json#/finegrained_rewith_test/3/test_cases/0/test_case"}
    assert "E2EDev_data/E2ESD_Bench_03/requirment_with_tests.json" in manifest["raw_files"]


def test_repeated_preparation_is_byte_stable_and_rejects_conflicting_output(dataset):
    source, output = dataset
    initial = prepare_e2edev(source, COMMIT, output)
    unit_path = output / "e2edev_bench_01.json"
    manifest_path = output / "manifests/e2edev.json"
    original_unit, original_manifest = unit_path.read_bytes(), manifest_path.read_bytes()
    assert prepare_e2edev(source, COMMIT, output) == initial
    assert unit_path.read_bytes() == original_unit
    assert manifest_path.read_bytes() == original_manifest

    conflicting_unit = b'{"id": "different_unit"}'
    unit_path.write_bytes(conflicting_unit)
    with pytest.raises(ValueError, match="E2EDev publication conflict"):
        prepare_e2edev(source, COMMIT, output)
    assert unit_path.read_bytes() == conflicting_unit
    assert manifest_path.read_bytes() == original_manifest


def test_rejects_an_unsupported_commit_before_publication(dataset):
    source, output = dataset
    with pytest.raises(ValueError, match="Unsupported E2EDev commit"):
        prepare_e2edev(source, "f" * 40, output)
    assert not output.exists()


def test_rejects_modified_annotation_before_first_publication(dataset):
    source, output = dataset
    annotation = _annotation(source, "01")
    _write_annotation(annotation, {"1": {"requirement": {"description": "Modified"}, "test_cases": []}})

    with pytest.raises(ValueError, match=r"E2EDev pinned annotation SHA-256 mismatch.*E2ESD_Bench_01"):
        prepare_e2edev(source, COMMIT, output)
    assert not output.exists()


def test_rejects_missing_benchmark_directory_before_first_publication(dataset):
    source, output = dataset
    e2edev.ANNOTATION_SHA256["02"] = "0" * 64
    assert not _annotation(source, "02").parent.exists()

    with pytest.raises(ValueError, match=r"E2EDev pinned annotation missing.*E2ESD_Bench_02"):
        prepare_e2edev(source, COMMIT, output)
    assert not output.exists()


def test_ignores_annotation_outside_pinned_inventory(dataset):
    source, output = dataset
    _write_annotation(
        _annotation(source, "99"),
        {"1": {"requirement": {"description": "Unexpected benchmark"}, "test_cases": []}},
    )

    units = prepare_e2edev(source, COMMIT, output)

    assert [unit.id for unit in units] == ["e2edev_bench_01"]
    assert len(_manifest(output)["raw_files"]) == 1
    assert not (output / "e2edev_bench_99.json").exists()
