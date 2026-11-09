"""Normalize local E2EDev requirement and Gherkin annotations."""

import hashlib
import json
import re
from pathlib import Path

from schemas import ReferenceCase, Requirement, Unit

from ._publication import publish

SOURCE_URL = "https://github.com/SCUNLP/E2EDev"
SOURCE_COMMIT = "d280dd144fbff30c237af26c1a76948e2f8857fa"
ANNOTATION = "requirment_with_tests.json"
REQUIREMENTS_KEY = "finegrained_rewith_test"
BENCHMARK_NAME = re.compile(r"E2ESD_Bench_([0-9]+)")
REQUIREMENT_KEY = re.compile(r"[1-9][0-9]*")
SCENARIO_HEADER = re.compile(r"^[ \t]*Scenario(?: Outline| Template)?:[ \t]*(\S.*)$", re.MULTILINE)
LINK_METHOD = "explicit_annotation"
LINK_STATUS = "source_annotated"


def _exclude(exclusions: list[dict], source: str, reason: str) -> None:
    exclusions.append({"source": source, "reason": reason})


def _read_annotation(
    path: Path, origin: str, raw_files: dict, exclusions: list[dict]
) -> dict | None:
    try:
        content = path.read_bytes()
    except FileNotFoundError:
        _exclude(exclusions, origin, "missing_annotation_file")
        return None
    except OSError:
        _exclude(exclusions, origin, "unreadable_annotation_file")
        return None

    raw_files[origin] = {"sha256": hashlib.sha256(content).hexdigest()}
    try:
        annotation = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _exclude(exclusions, origin, "invalid_annotation_json")
        return None

    rows = annotation.get(REQUIREMENTS_KEY) if isinstance(annotation, dict) else None
    if not isinstance(rows, dict):
        _exclude(exclusions, f"{origin}#/{REQUIREMENTS_KEY}", "invalid_requirement_mapping")
        return None
    return rows


def _reference_cases(
    test_cases: object, requirement_id: str, origin: str, exclusions: list[dict]
) -> list[ReferenceCase]:
    if not isinstance(test_cases, list):
        _exclude(exclusions, origin, "invalid_test_cases")
        return []

    cases = []
    for index, record in enumerate(test_cases):
        gherkin_source = f"{origin}/{index}/test_case"
        lines = record.get("test_case") if isinstance(record, dict) else None
        if not isinstance(lines, list) or not all(isinstance(line, str) for line in lines):
            _exclude(exclusions, gherkin_source, "invalid_gherkin")
            continue
        gherkin = "\n".join(lines)
        titles = SCENARIO_HEADER.findall(gherkin)
        if len(titles) != 1:
            _exclude(exclusions, gherkin_source, "invalid_gherkin")
            continue
        cases.append(
            ReferenceCase(
                id=f"{requirement_id}-TC-{index + 1}",
                title=titles[0].strip(),
                description=gherkin,
                requirement_ids=[requirement_id],
                source=gherkin_source,
                link_method=LINK_METHOD,
                link_status=LINK_STATUS,
            )
        )
    return cases


def _benchmark_unit(
    unit_id: str, rows: dict, origin: str, exclusions: list[dict]
) -> Unit | None:
    requirements = []
    cases = []
    for key, row in sorted(rows.items(), key=lambda item: (len(item[0]), item[0])):
        pointer_key = key.replace("~", "~0").replace("/", "~1")
        row_source = f"{origin}#/{REQUIREMENTS_KEY}/{pointer_key}"
        if not REQUIREMENT_KEY.fullmatch(key):
            _exclude(exclusions, row_source, "invalid_requirement_key")
            continue
        requirement = row.get("requirement") if isinstance(row, dict) else None
        text = requirement.get("description") if isinstance(requirement, dict) else None
        text_source = f"{row_source}/requirement/description"
        if not isinstance(text, str) or not text.strip():
            _exclude(exclusions, text_source, "invalid_requirement_description")
            continue

        requirement_id = f"{unit_id}-R-{key}"
        requirements.append(Requirement(id=requirement_id, text=text, language="en", source=text_source))
        cases_source = f"{row_source}/test_cases"
        if "test_cases" not in row:
            _exclude(exclusions, cases_source, "missing_test_cases")
            continue
        cases.extend(_reference_cases(row["test_cases"], requirement_id, cases_source, exclusions))

    if not requirements:
        _exclude(exclusions, f"{origin}#/{REQUIREMENTS_KEY}", "no_valid_requirements")
        return None
    return Unit(id=unit_id, requirements=requirements, reference_cases=cases)


def prepare_e2edev(source: Path, commit: str, output: Path) -> list[Unit]:
    """Read the pinned annotation format from a local repository snapshot."""
    if commit != SOURCE_COMMIT:
        raise ValueError(f"Unsupported E2EDev commit {commit!r}. Expected {SOURCE_COMMIT}.")
    data = source / "E2EDev_data"
    if not data.is_dir():
        raise ValueError(f"E2EDev annotations directory not found: {data}")

    units = []
    raw_files: dict = {}
    exclusions: list[dict] = []
    for benchmark in sorted(data.iterdir()):
        name = BENCHMARK_NAME.fullmatch(benchmark.name)
        if name is None or not benchmark.is_dir():
            continue
        path = benchmark / ANNOTATION
        origin = path.relative_to(source).as_posix()
        rows = _read_annotation(path, origin, raw_files, exclusions)
        if rows is None:
            continue
        unit = _benchmark_unit(f"e2edev_bench_{name[1]}", rows, origin, exclusions)
        if unit is not None:
            units.append(unit)

    manifest = {
        "dataset_id": "e2edev",
        "source": {
            "url": SOURCE_URL,
            "commit": commit,
            "license": None,
            "license_observation": {
                "status": "unverified",
                "root_license_or_copying_files": [],
                "readme_declares_license": False,
            },
            "acquisition_method": "git_sparse_checkout",
        },
        "adapter": "datasets.e2edev.prepare_e2edev",
        "annotation_path": f"E2EDev_data/E2ESD_Bench_*/{ANNOTATION}",
        "raw_files": raw_files,
        "units": [
            {
                "id": unit.id,
                "requirements": len(unit.requirements),
                "reference_cases": len(unit.reference_cases),
            }
            for unit in units
        ],
        "links": {"method": LINK_METHOD, "status": LINK_STATUS, "ambiguous": []},
        "excluded_fields": ["summary", "step_code"],
        "exclusions": exclusions,
    }
    artifacts = {
        **{Path(f"{unit.id}.json"): unit.model_dump(mode="json") for unit in units},
        Path("manifests/e2edev.json"): manifest,
    }
    publish(
        output,
        {
            path: (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            for path, payload in artifacts.items()
        },
        dataset="E2EDev",
    )
    return units
