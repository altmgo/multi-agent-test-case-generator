"""Normalize the local Mendeley Data v1 Firefox requirement and test exports."""

import csv
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from schemas import ReferenceCase, Requirement, Unit

PAIR_COUNT = 184
ARCHIVE_ID = "firefox_legacy"
LINK_METHOD = "inferred_row_alignment"
LINK_STATUS = "pending_provenance_review"
MANIFEST_PATH = Path("manifests/firefox_bookmarks.json")

PARTITIONS = (
    ("firefox_bookmarks", 1, 18),
    ("firefox_clipboard_and_drag_drop", 19, 37),
    ("firefox_form_manager", 38, 45),
    ("firefox_help", 46, 72),
    ("firefox_browser_history", 73, 84),
    ("firefox_image_and_embedded_content", 85, 101),
    ("firefox_password_manager", 102, 108),
    ("firefox_printing", 109, 131),
    ("firefox_media_plugins", 132, 134),
    ("firefox_search", 135, 139),
    ("firefox_text_selection", 140, 143),
    ("firefox_sidebar", 144, 165),
    ("firefox_web_location", 166, 174),
    ("firefox_themes", 175, 181),
    ("firefox_toolbar", 182, 184),
)

# Secondary labels are pinned to the v1 IDs and checked against both source
# texts. An incidental mention in setup or a link does not establish a domain.
SECONDARY_CASES = {
    "firefox_bookmarks": (36, 37, 139, 162),
    "firefox_clipboard_and_drag_drop": (18, 53),
    "firefox_image_and_embedded_content": (21, 23, 24, 25, 26, 27, 31, 122),
    "firefox_printing": (55, 56, 57, 58, 59, 60, 61, 89),
    "firefox_sidebar": (136, 137),
    "firefox_web_location": (35, 136),
    "firefox_toolbar": (3, 51),
}


def _read_csv(
    path: Path, headers: tuple[str, str], prefix: str
) -> tuple[list[tuple[str, str]], str]:
    content = path.read_bytes()
    try:
        stream = io.StringIO(content.decode("utf-8-sig"), newline="")
    except UnicodeDecodeError as error:
        raise ValueError(f"{path}: expected UTF-8 CSV: {error}") from error

    reader = csv.reader(stream, delimiter=";", strict=True)
    rows = []
    try:
        header = next(reader, [])
        if tuple(header) != headers:
            raise ValueError(f"{path}: expected columns {headers}, found {header}")
        for row in reader:
            if len(row) != len(headers):
                raise ValueError(
                    f"{path}, line {reader.line_num}: expected 2 columns, found {len(row)}"
                )
            identifier, text = row
            rows.append((identifier, text))
    except csv.Error as error:
        raise ValueError(f"{path}, line {reader.line_num}: invalid CSV: {error}") from error

    if len(rows) != PAIR_COUNT:
        raise ValueError(f"{path}: expected {PAIR_COUNT} records, found {len(rows)}")
    for number, (identifier, _) in enumerate(rows, 1):
        expected = f"{prefix}-{number:03}"
        if identifier != expected:
            raise ValueError(
                f"{path}, record {number}: expected {expected}, found {identifier!r}"
            )
    return rows, hashlib.sha256(content).hexdigest()


def _feature_unit(
    partition: tuple[str, int, int],
    requirements_file: Path,
    tests_file: Path,
    requirement_rows: list[tuple[str, str]],
    test_rows: list[tuple[str, str]],
) -> Unit:
    unit_id, first, last = partition
    requirements = []
    reference_cases = []
    aligned_rows = zip(requirement_rows[first - 1 : last], test_rows[first - 1 : last], strict=True)
    for number, ((requirement_id, text), (case_id, description)) in enumerate(aligned_rows, first):
        requirements.append(
            Requirement(
                id=requirement_id,
                text=text,
                language="en",
                source=f"{requirements_file.name}#{requirement_id}",
            )
        )
        reference_cases.append(
            ReferenceCase(
                id=case_id,
                title=case_id,
                description=description,
                requirement_ids=[requirement_id],
                source=f"{tests_file.name}#{case_id}",
                link_method=LINK_METHOD,
                link_status=LINK_STATUS,
                secondary_domains=[
                    domain for domain, numbers in SECONDARY_CASES.items() if number in numbers
                ],
            )
        )
    return Unit(
        id=unit_id,
        parent_id=ARCHIVE_ID,
        requirements=requirements,
        reference_cases=reference_cases,
    )


def _manifest(requirements: Path, tests: Path, requirement_hash: str, test_hash: str) -> dict:
    return {
        "dataset_id": ARCHIVE_ID,
        "source": {
            "repository": "Mendeley Data",
            "url": "https://data.mendeley.com/datasets/jw5bgshtvg/1",
            "version": 1,
            "doi": "10.17632/jw5bgshtvg.1",
            "license": "CC BY 4.0",
            "acquisition_method": "user_supplied_local_csv",
        },
        "raw_files": {
            "requirements": {"filename": requirements.name, "sha256": requirement_hash},
            "tests": {"filename": tests.name, "sha256": test_hash},
        },
        "adapter": "datasets.firefox.prepare_firefox",
        "pair_count": PAIR_COUNT,
        "archive_generatable": False,
        "links": {
            "method": LINK_METHOD,
            "status": LINK_STATUS,
            "pending_review_count": PAIR_COUNT,
        },
        "title_origin": "source_case_id",
        "exclusions": [],
        "taxonomy": {
            "version": 1,
            "partitions": [
                {
                    "unit_id": unit_id,
                    "first_requirement_id": f"R-{first:03}",
                    "last_requirement_id": f"R-{last:03}",
                }
                for unit_id, first, last in PARTITIONS
            ],
            "secondary_case_ids": {
                domain: [f"TC-{number:03}" for number in numbers]
                for domain, numbers in SECONDARY_CASES.items()
            },
        },
    }


def prepare_firefox(requirements: Path, tests: Path, output: Path) -> list[Unit]:
    """Write the archival unit, feature units, and provenance manifest to output."""
    requirement_rows, requirement_hash = _read_csv(
        requirements, ("RequirementID", "RequirementContent"), "R"
    )
    test_rows, test_hash = _read_csv(tests, ("TestCaseID", "TestCaseContent"), "TC")
    features = [
        _feature_unit(partition, requirements, tests, requirement_rows, test_rows)
        for partition in PARTITIONS
    ]
    archive = Unit(
        id=ARCHIVE_ID,
        generatable=False,
        requirements=[requirement for unit in features for requirement in unit.requirements],
        reference_cases=[case for unit in features for case in unit.reference_cases],
    )
    units = [archive, *features]
    manifest = _manifest(requirements, tests, requirement_hash, test_hash)
    artifacts = {
        **{Path(f"{unit.id}.json"): unit.model_dump(mode="json") for unit in units},
        MANIFEST_PATH: manifest,
    }

    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as staging:
        for relative_path, data in artifacts.items():
            path = Path(staging) / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for relative_path in artifacts:
            target = output / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            (Path(staging) / relative_path).replace(target)
    return units
