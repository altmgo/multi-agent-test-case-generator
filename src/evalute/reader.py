"""Read final cases from a TCG run and their reference data."""

import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.tcg.output import _id_component, _markdown_inline
from src.tcg.schemas import GeneratedCase, UsageRecord, generation_input, validate_cases

from .models import EvaluationUnit

SOLUTIONS = {"one-shot", "GHL", "Multiagent"}
_UNIT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}")
_CASE_FILE = re.compile(r"([1-9][0-9]*)_.+\.md")
_UNESCAPE = re.compile(r"\\([\\\x60*_{}\[\]()<>#+!|])")


@dataclass
class GeneratedUnit:
    solution: str
    path: Path
    dataset: EvaluationUnit
    cases: list[GeneratedCase]
    usage: UsageRecord
    generation: dict
    failure: dict[str, str] | None
    links: dict
    intermediate: dict


def _text(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")
    return path.read_bytes().decode("utf-8")


def _directory(path: Path) -> None:
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"Expected a regular directory: {path}")


def read_config(run: Path) -> dict:
    fence = chr(96) * 3
    _, separator, document = _text(run / "configs.md").partition(f"\n{fence}json\n")
    ending = f"\n{fence}"
    if not separator or not document.rstrip().endswith(ending):
        raise ValueError("Expected configs.md from a TCG run")
    config = json.loads(document.rstrip().removesuffix(ending))
    if not isinstance(config, dict):
        raise ValueError("Expected a JSON object in configs.md")
    return config


def _case(path: Path) -> GeneratedCase:
    parts = _text(path).split("\n\n", 3)
    prefixes = ("# ", "Case ID · ", "Requirements · ")
    if len(parts) != 4 or any(not text.startswith(prefix) for text, prefix in zip(parts[:3], prefixes)):
        raise ValueError(f"Invalid TCG case Markdown: {path}")
    title, case_id, requirement_ids = (
        _UNESCAPE.sub(r"\1", text.removeprefix(prefix))
        for text, prefix in zip(parts[:3], prefixes)
    )
    return GeneratedCase(
        id=case_id, title=title, description=parts[3].removesuffix("\n"),
        requirement_ids=requirement_ids.split(", "),
    )


def _read_cases(unit: EvaluationUnit, directory: Path) -> tuple[list[GeneratedCase], dict]:
    requirements = {}
    cases = {}
    links: dict[str, dict[str, str]] = {}
    order: dict[str, int] = {}
    for requirement in unit.requirements:
        parent = directory / _id_component(requirement.id)
        _directory(parent)
        requirement_file = parent / "requirement.md"
        expected = f"# {_markdown_inline(requirement.id)}\n\n{requirement.text}\n"
        if _text(requirement_file) != expected:
            raise ValueError(f"Requirement differs from the normalized dataset: {requirement_file}")
        requirements[requirement.id] = requirement_file.relative_to(directory).as_posix()

        case_dir = parent / "test cases"
        _directory(case_dir)
        for path in sorted(case_dir.glob("*.md")):
            filename = _CASE_FILE.fullmatch(path.name)
            if filename is None:
                raise ValueError(f"Unexpected case filename: {path}")
            case = _case(path)
            sequence = int(filename[1])
            if requirement.id not in case.requirement_ids:
                raise ValueError(f"Case does not link to its requirement directory: {path}")
            if case.id in cases and (cases[case.id] != case or order[case.id] != sequence):
                raise ValueError(f"Conflicting copies of case {case.id}: {path}")
            cases[case.id] = case
            order[case.id] = sequence
            destinations = links.setdefault(case.id, {})
            if requirement.id in destinations:
                raise ValueError(f"Duplicate case for requirement: {path}")
            destinations[requirement.id] = path.relative_to(directory).as_posix()

    if len(set(order.values())) != len(order):
        raise ValueError(f"Duplicate case sequence numbers: {directory}")
    generated = sorted(cases.values(), key=lambda case: order[case.id])
    validate_cases(generation_input(unit), generated)
    if any(set(case.requirement_ids) != links[case.id].keys() for case in generated):
        raise ValueError(f"Missing Markdown case copies: {directory}")
    return generated, {"requirements": requirements, "cases": links}


def _intermediate(directory: Path) -> dict:
    path = directory / "intermediate/trace.json"
    if not path.is_file():
        return {}
    _directory(path.parent)
    trace = json.loads(_text(path))
    rounds = []
    for revision in trace["rounds"]:
        prefix = f"intermediate/round_{revision['number']:03d}"
        rounds.append({
            "decision": f"{prefix}/decision.json",
            "attempts": [f"{prefix}/attempt_{n}.json" for n in range(1, len(revision["candidates"]) + 1)],
        })
    return {"trace": "intermediate/trace.json", "initial": "intermediate/initial.json", "rounds": rounds}


def read_generated_unit(run: Path, data_dir: Path, solution: str, unit_id: str, outcome: dict) -> GeneratedUnit:
    if solution not in SOLUTIONS or not _UNIT_ID.fullmatch(unit_id):
        raise ValueError("Invalid solution or unit in configs.md")
    directory = run / solution / _id_component(unit_id)
    _directory(directory.parent)
    _directory(directory)
    for name in ("results.json", "results.csv", "semantic_matches.json"):
        target = directory / name
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError(f"Invalid result destination: {target}")
    previous = directory / "results.json"
    if previous.exists():
        snapshot = json.loads(_text(previous))
        if "human_evaluation" in snapshot or "human_evaluation_history" in snapshot:
            raise ValueError(f"Refusing to replace human review: {previous}")

    unit = EvaluationUnit.model_validate_json(_text(data_dir / f"{unit_id}.json"))
    if unit.id != unit_id or not unit.generatable:
        raise ValueError(f"Ineligible or mismatched normalized unit: {unit_id}")
    requirement_ids = {item.id for item in unit.requirements}
    if len(requirement_ids) != len(unit.requirements):
        raise ValueError(f"Duplicate requirement IDs: {unit_id}")
    if len({case.id for case in unit.reference_cases}) != len(unit.reference_cases) or any(
        not requirement_ids.issuperset(case.requirement_ids) for case in unit.reference_cases
    ):
        raise ValueError(f"Invalid reference IDs or links: {unit_id}")

    cases, links = _read_cases(unit, directory)
    if len(cases) != outcome["case_count"]:
        raise ValueError(f"Case count differs from configs.md: {directory}")
    status = outcome["status"]
    if status not in {"generated", "failed", "interrupted"}:
        raise ValueError(f"Invalid generation status: {status}")
    failure = None if status == "generated" else {
        "stage": "generation", "error_type": outcome.get("error_type") or status,
    }
    return GeneratedUnit(
        solution=solution, path=directory, dataset=unit, cases=cases,
        usage=UsageRecord.model_validate(outcome.get("usage", {})),
        generation={
            "selected_techniques": outcome.get("selected_techniques", []),
            "technique_rationales": outcome.get("technique_rationales", {}),
            "prompt_version": outcome.get("prompt_version"),
        },
        failure=failure, links=links, intermediate=_intermediate(directory),
    )
