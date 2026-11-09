import csv
import hashlib
import json
from pathlib import Path

import pytest

from datasets.firefox import prepare_firefox
from schemas import Unit, generation_input

FEATURE_RANGES = {
    "firefox_bookmarks": (1, 18),
    "firefox_clipboard_and_drag_drop": (19, 37),
    "firefox_form_manager": (38, 45),
    "firefox_help": (46, 72),
    "firefox_browser_history": (73, 84),
    "firefox_image_and_embedded_content": (85, 101),
    "firefox_password_manager": (102, 108),
    "firefox_printing": (109, 131),
    "firefox_media_plugins": (132, 134),
    "firefox_search": (135, 139),
    "firefox_text_selection": (140, 143),
    "firefox_sidebar": (144, 165),
    "firefox_web_location": (166, 174),
    "firefox_themes": (175, 181),
    "firefox_toolbar": (182, 184),
}

REQUIREMENT_TEXT = '  Preserve "café"; exactly.\r\nSecond line.  '
CASE_TEXT = 'First step; open "café".\n\n  Expected result: unchanged.  '


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(header)
        writer.writerows(rows)


@pytest.fixture
def source_csvs(tmp_path):
    requirement_rows = [(f"R-{n:03}", f"Requirement {n}") for n in range(1, 185)]
    case_rows = [(f"TC-{n:03}", f"Case {n}") for n in range(1, 185)]
    requirement_rows[0] = ("R-001", REQUIREMENT_TEXT)
    case_rows[0] = ("TC-001", CASE_TEXT)
    requirement_rows[2] = ("R-003", "Add a bookmark through the toolbar.")
    case_rows[2] = ("TC-003", "Check the bookmark is visible in the toolbar.")

    requirements = tmp_path / "R-set.csv"
    tests = tmp_path / "T-set.csv"
    write_csv(requirements, ("RequirementID", "RequirementContent"), requirement_rows)
    write_csv(tests, ("TestCaseID", "TestCaseContent"), case_rows)
    return requirements, tests


def test_preserves_csv_content_and_original_links(source_csvs, tmp_path):
    output = tmp_path / "normalized"
    units = prepare_firefox(*source_csvs, output)
    bookmarks = next(unit for unit in units if unit.id == "firefox_bookmarks")

    assert bookmarks.requirements[0].model_dump() == {
        "id": "R-001",
        "text": REQUIREMENT_TEXT,
        "language": "en",
        "source": "R-set.csv#R-001",
    }
    assert bookmarks.reference_cases[0].model_dump() == {
        "id": "TC-001",
        "title": "TC-001",
        "description": CASE_TEXT,
        "requirement_ids": ["R-001"],
        "source": "T-set.csv#TC-001",
        "link_method": "inferred_row_alignment",
        "link_status": "pending_provenance_review",
        "secondary_domains": [],
    }
    stored = Unit.model_validate_json((output / "firefox_bookmarks.json").read_bytes())
    assert stored == bookmarks


def test_partitions_all_pairs_and_excludes_archive_from_generation(source_csvs, tmp_path):
    output = tmp_path / "normalized"
    units = prepare_firefox(*source_csvs, output)
    archive, *features = units
    assert archive.id == "firefox_legacy"
    assert archive.parent_id is None
    assert Unit.model_validate_json((output / "firefox_legacy.json").read_bytes()) == archive
    with pytest.raises(ValueError, match="firefox_legacy"):
        generation_input(archive)

    assert len(features) == 15
    assert {unit.id for unit in features} == set(FEATURE_RANGES)
    all_requirements = []
    all_cases = []
    for unit in features:
        assert Unit.model_validate_json((output / f"{unit.id}.json").read_bytes()) == unit
        first, last = FEATURE_RANGES[unit.id]
        assert unit.parent_id == archive.id
        assert [item.id for item in generation_input(unit).requirements] == [
            f"R-{n:03}" for n in range(first, last + 1)
        ]
        assert [(case.id, case.requirement_ids) for case in unit.reference_cases] == [
            (f"TC-{n:03}", [f"R-{n:03}"]) for n in range(first, last + 1)
        ]
        all_requirements.extend(unit.requirements)
        all_cases.extend(unit.reference_cases)

    assert len({item.id for item in all_requirements}) == 184
    assert len({case.id for case in all_cases}) == 184
    assert sorted(all_requirements, key=lambda item: item.id) == archive.requirements
    assert sorted(all_cases, key=lambda case: case.id) == archive.reference_cases

    bookmarks = next(unit for unit in features if unit.id == "firefox_bookmarks")
    toolbar = next(unit for unit in features if unit.id == "firefox_toolbar")
    assert bookmarks.reference_cases[2].secondary_domains == ["firefox_toolbar"]
    assert "TC-003" not in {case.id for case in toolbar.reference_cases}


def test_writes_deterministic_metadata_without_csv_text(source_csvs, tmp_path):
    output = tmp_path / "normalized"
    prepare_firefox(*source_csvs, output)
    manifest_path = output / "manifests" / "firefox_bookmarks.json"
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest["source"]["version"] == 1
    assert manifest["source"]["doi"] == "10.17632/jw5bgshtvg.1"
    assert manifest["source"]["url"] == "https://data.mendeley.com/datasets/jw5bgshtvg/1"
    assert manifest["adapter"] == "datasets.firefox.prepare_firefox"
    assert manifest["title_origin"] == "source_case_id"
    assert manifest["pair_count"] == 184
    assert manifest["links"] == {
        "method": "inferred_row_alignment",
        "status": "pending_provenance_review",
        "pending_review_count": 184,
    }
    assert manifest["exclusions"] == []
    assert manifest["taxonomy"]["version"]
    assert {
        part["unit_id"]: (part["first_requirement_id"], part["last_requirement_id"])
        for part in manifest["taxonomy"]["partitions"]
    } == {
        unit_id: (f"R-{first:03}", f"R-{last:03}")
        for unit_id, (first, last) in FEATURE_RANGES.items()
    }
    assert manifest["raw_files"] == {
        role: {"filename": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for role, path in zip(("requirements", "tests"), source_csvs, strict=True)
    }
    assert "Preserve" not in manifest_path.read_text()
    assert "Expected result" not in manifest_path.read_text()

    initial = {path: path.read_bytes() for path in output.rglob("*.json")}
    prepare_firefox(*source_csvs, output)
    assert {path: path.read_bytes() for path in output.rglob("*.json")} == initial


def test_manifest_preserves_both_sources_with_the_same_filename(source_csvs, tmp_path):
    requirements, tests = source_csvs
    tests_folder = tmp_path / "tests-source"
    tests_folder.mkdir()
    tests = tests.rename(tests_folder / requirements.name)
    output = tmp_path / "normalized"

    prepare_firefox(requirements, tests, output)
    manifest = json.loads((output / "manifests" / "firefox_bookmarks.json").read_bytes())
    assert manifest["raw_files"] == {
        "requirements": {
            "filename": "R-set.csv",
            "sha256": hashlib.sha256(requirements.read_bytes()).hexdigest(),
        },
        "tests": {
            "filename": "R-set.csv",
            "sha256": hashlib.sha256(tests.read_bytes()).hexdigest(),
        },
    }


@pytest.mark.parametrize(
    ("file_index", "defect", "error"),
    [
        (0, "missing", r"R-set\.csv.*expected 184.*found 183"),
        (1, "extra", r"T-set\.csv.*expected 184.*found 185"),
        (0, "duplicate", r"R-set\.csv.*expected R-002.*found 'R-001'"),
        (1, "reordered", r"T-set\.csv.*expected TC-002.*found 'TC-003'"),
        (1, "malformed_row", r"T-set\.csv.*expected 2 columns.*found 3"),
    ],
)
def test_rejects_misaligned_inputs_before_writing(source_csvs, tmp_path, file_index, defect, error):
    path = source_csvs[file_index]
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header, *rows = csv.reader(stream, delimiter=";")
    if defect == "missing":
        rows.pop()
    elif defect == "extra":
        rows.append(["TC-185", "extra case"])
    elif defect == "duplicate":
        rows[1][0] = "R-001"
    elif defect == "reordered":
        rows[1], rows[2] = rows[2], rows[1]
    else:
        rows[1].append("unexpected column")
    write_csv(path, header, rows)

    output = tmp_path / "normalized"
    with pytest.raises(ValueError, match=error):
        prepare_firefox(*source_csvs, output)
    assert not output.exists()


def test_matches_provided_firefox_csvs_when_available(tmp_path):
    raw = Path(__file__).resolve().parents[1] / "data" / "raw" / "firefox"
    requirements, tests = raw / "R-set.csv", raw / "T-set.csv"
    if not requirements.exists() and not tests.exists():
        pytest.skip("local Firefox CSVs are unavailable")
    units = prepare_firefox(requirements, tests, tmp_path / "normalized")
    archive, *features = units
    with requirements.open(encoding="utf-8-sig", newline="") as stream:
        expected_requirements = list(csv.reader(stream, delimiter=";"))[1:]
    with tests.open(encoding="utf-8-sig", newline="") as stream:
        expected_cases = list(csv.reader(stream, delimiter=";"))[1:]
    assert [(item.id, item.text) for item in archive.requirements] == [
        tuple(row) for row in expected_requirements
    ]
    assert [(case.id, case.description) for case in archive.reference_cases] == [
        tuple(row) for row in expected_cases
    ]
    bookmarks = next(unit for unit in features if unit.id == "firefox_bookmarks")
    assert bookmarks.reference_cases[2].secondary_domains == ["firefox_toolbar"]
    assert bookmarks.reference_cases[17].secondary_domains == ["firefox_clipboard_and_drag_drop"]
    assert len(archive.requirements) == len(archive.reference_cases) == 184
