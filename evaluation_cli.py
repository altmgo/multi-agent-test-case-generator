"""Evaluate a persisted experiment without regenerating any cases."""

import argparse
import fcntl
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, NonNegativeInt

from evaluation.embeddings import EMBEDDING_MODEL, Embedder, EmbeddingError, GeminiEmbedder
from evaluation.metrics import aggregate, evaluate
from persistence import RESULT_SCHEMA_VERSION, SOLUTIONS, _id_component, update_evaluation, write_json, write_text
from schemas import EvaluationResult, GeneratedCase, Identifier, ReferenceCase, Requirement, Unit, UsageRecord


class _Usage(BaseModel):
    generation: UsageRecord
    embedding: UsageRecord
    embedding_requests: NonNegativeInt | None


class _Links(BaseModel):
    requirements: dict[str, str]
    cases: dict[str, dict[str, str]]


class _Snapshot(BaseModel):
    schema_version: int = Field(strict=True, ge=RESULT_SCHEMA_VERSION, le=RESULT_SCHEMA_VERSION)
    solution: Literal["one-shot", "GHL", "Multiagent"]
    unit_id: Identifier
    parent_id: Identifier | None
    requirements: list[Requirement]
    generated_cases: list[GeneratedCase]
    reference_cases: list[ReferenceCase]
    status: Literal["generated", "evaluated", "not_evaluable", "failed"]
    failure: dict[str, str] | None
    evaluation: EvaluationResult | None
    usage: _Usage
    links: _Links
    artifacts: dict[str, object]


@dataclass(frozen=True)
class _SavedUnit:
    path: Path
    original: bytes
    snapshot: _Snapshot


def make_embedder() -> Embedder:
    return GeminiEmbedder(model_version=EMBEDDING_MODEL)


def _name(value: str) -> None:
    if not value or value in {".", ".."} or "/" in value or "\\" in value or Path(value).is_absolute():
        raise ValueError("Select a single run, solution, or unit name")


def _no_symlinks(path: Path) -> None:
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("Artifact paths cannot be symbolic links")


def _linked_file(directory: Path, relative: str) -> None:
    target = Path(relative)
    if target.is_absolute() or ".." in target.parts or "\\" in relative:
        raise ValueError("An artifact link leaves the unit directory")
    path = directory / target
    _no_symlinks(path)
    if not path.is_file():
        raise ValueError("An artifact link refers to a missing file")


def _validate(saved: _SavedUnit) -> None:
    snapshot = saved.snapshot
    directory = saved.path.parent
    requirements = {requirement.id for requirement in snapshot.requirements}
    generated = {case.id for case in snapshot.generated_cases}
    references = {case.id for case in snapshot.reference_cases}
    if (len(requirements) != len(snapshot.requirements) or len(generated) != len(snapshot.generated_cases)
            or len(references) != len(snapshot.reference_cases)):
        raise ValueError("Duplicate IDs in a unit snapshot")
    for case in [*snapshot.generated_cases, *snapshot.reference_cases]:
        if not set(case.requirement_ids) <= requirements:
            raise ValueError("A case links to a missing requirement")
    if snapshot.links.requirements.keys() != requirements or snapshot.links.cases.keys() != generated:
        raise ValueError("Inconsistent requirement or case links")
    for relative in snapshot.links.requirements.values():
        _linked_file(directory, relative)
    for case in snapshot.generated_cases:
        links = snapshot.links.cases[case.id]
        if links.keys() != set(case.requirement_ids):
            raise ValueError("Inconsistent generated case links")
        for relative in links.values():
            _linked_file(directory, relative)
    if (snapshot.artifacts.get("csv") != "results.csv"
            or snapshot.artifacts.get("semantic_matches") != "semantic_matches.json"):
        raise ValueError("Unsupported derived artifact links")
    for filename in ("results.csv", "semantic_matches.json"):
        _no_symlinks(directory / filename)

    automatic = snapshot.evaluation
    if snapshot.status in {"generated", "failed"}:
        if automatic is not None or (snapshot.status == "failed") != (snapshot.failure is not None):
            raise ValueError("Inconsistent unit status, failure, or evaluation")
        if snapshot.failure is not None and not {"stage", "error_type"} <= snapshot.failure.keys():
            raise ValueError("Incomplete failure metadata")
        return
    if (automatic is None or snapshot.failure is not None or automatic.status != snapshot.status
            or (automatic.status == "evaluated") != bool(references)
            or automatic.generated_count != len(generated) or automatic.reference_count != len(references)):
        raise ValueError("Inconsistent automatic evaluation or counts")
    matched_generated = [match.generated_id for match in automatic.matches]
    matched_references = [match.reference_id for match in automatic.matches]
    for matched, unmatched, available in (
        (matched_generated, automatic.unmatched_generated_ids, generated),
        (matched_references, automatic.unmatched_reference_ids, references),
    ):
        if (len(set(matched)) != len(matched) or len(set(unmatched)) != len(unmatched)
                or set(matched) & set(unmatched) or set(matched) | set(unmatched) != available):
            raise ValueError("Automatic matches and unmatched IDs must partition the cases")
    if any(not math.isfinite(match.similarity) for match in automatic.matches):
        raise ValueError("Automatic match similarity must be finite")


def _load_run(run: Path) -> tuple[dict, dict[str, dict[str, _SavedUnit]]]:
    _no_symlinks(run)
    if not run.is_dir():
        raise ValueError("Unknown run")
    for filename in ("configs.md", "comparison.json"):
        _no_symlinks(run / filename)
    text = (run / "configs.md").read_text(encoding="utf-8")
    try:
        config = json.loads(text.split("```json\n", 1)[1].split("\n```", 1)[0])
        json.dumps(config, ensure_ascii=False, allow_nan=False)
    except (IndexError, ValueError) as error:
        raise ValueError("Invalid experiment configuration") from error
    if (not isinstance(config, dict) or not isinstance(config.get("solutions"), list)
            or not config["solutions"] or any(solution not in SOLUTIONS for solution in config["solutions"])
            or len(set(config["solutions"])) != len(config["solutions"])
            or not isinstance(config.get("units"), dict) or not config["units"]):
        raise ValueError("Invalid configured solutions or units")
    for unit_id in config["units"]:
        _name(unit_id)
    units: dict[str, dict[str, _SavedUnit]] = {solution: {} for solution in config["solutions"]}
    for solution_dir in sorted(run.iterdir()):
        if solution_dir.is_symlink():
            raise ValueError("Artifact paths cannot be symbolic links")
        if not solution_dir.is_dir():
            continue
        if solution_dir.name not in units:
            raise ValueError("Unknown solution directory")
        for directory in sorted(solution_dir.iterdir()):
            _no_symlinks(directory)
            if not directory.is_dir():
                continue
            path = directory / "results.json"
            _no_symlinks(path)
            original = path.read_bytes()
            json.dumps(json.loads(original), ensure_ascii=False, allow_nan=False)
            snapshot = _Snapshot.model_validate_json(original, strict=True)
            if (snapshot.solution != solution_dir.name or snapshot.unit_id not in config["units"]
                    or directory.name != _id_component(snapshot.unit_id)):
                raise ValueError("Snapshot does not belong to its configured solution or unit")
            if snapshot.unit_id in units[solution_dir.name]:
                raise ValueError("Duplicate unit ID in one solution")
            saved = _SavedUnit(path, original, snapshot)
            _validate(saved)
            units[solution_dir.name][snapshot.unit_id] = saved
    return config, units


def evaluate_run(run: Path, solution: str | None = None, unit_id: str | None = None) -> int:
    """Evaluate selected snapshots and refresh the comparison for the whole run."""
    config, units = _load_run(run)
    if solution is not None:
        _name(solution)
        solution = next((name for name in units if name.casefold() == solution.casefold()), None)
        if solution is None:
            raise ValueError("Unknown solution")
    if unit_id is not None:
        _name(unit_id)
        if unit_id not in config["units"] or not any(
            unit_id in available for name, available in units.items() if solution is None or name == solution
        ):
            raise ValueError("Unknown unit")
    selected = [
        saved for name, available in units.items() if solution is None or name == solution
        for identifier, saved in available.items() if unit_id is None or identifier == unit_id
        if saved.snapshot.status != "failed" or saved.snapshot.failure["stage"] == "evaluation"
    ]
    embedder = None
    failures = 0
    close_failed = False
    try:
        for saved in selected:
            snapshot = saved.snapshot
            automatic = failure = None
            embedding_usage, embedding_requests = None, None
            try:
                if embedder is None:
                    embedder = make_embedder()
                unit = Unit(id=snapshot.unit_id, parent_id=snapshot.parent_id, requirements=snapshot.requirements,
                            reference_cases=snapshot.reference_cases)
                automatic = evaluate(unit, snapshot.generated_cases, embedder)
            except Exception as error:
                failure = {"stage": "evaluation", "error_type": type(error).__name__}
                if isinstance(error, EmbeddingError):
                    embedding_usage, embedding_requests = error.usage, error.request_count
            try:
                update_evaluation(saved.path, saved.original, automatic, failure=failure,
                                  embedding_usage=embedding_usage, embedding_requests=embedding_requests)
            except (OSError, ValueError) as error:
                failure = {"stage": "persistence", "error_type": type(error).__name__}
            if failure is not None:
                failures += 1
                print(f"{snapshot.solution}/{snapshot.unit_id}: {failure['stage']} failed ({failure['error_type']})", file=sys.stderr)
    finally:
        if embedder is not None and (close := getattr(embedder, "close", None)) is not None:
            try:
                close()
            except Exception as error:
                close_failed = True
                print(f"Embedding transport close failed ({type(error).__name__}).", file=sys.stderr)

    run_fd = os.open(run, os.O_RDONLY)
    try:
        # Reload under the publication lock so a later writer cannot publish older totals.
        fcntl.flock(run_fd, fcntl.LOCK_EX)
        config, units = _load_run(run)
        evaluations = {name: {} for name in units}
        outcomes = {name: {} for name in units}
        for name, available in units.items():
            for identifier in config["units"]:
                saved = available.get(identifier)
                if saved is None:
                    outcomes[name][identifier] = config.get("outcomes", {}).get(name, {}).get(
                        identifier, {"status": "missing"}
                    )
                    continue
                snapshot = saved.snapshot
                outcomes[name][identifier] = {"status": snapshot.status}
                if snapshot.failure is not None:
                    outcomes[name][identifier]["failure"] = snapshot.failure
                if snapshot.evaluation is not None:
                    evaluations[name][identifier] = snapshot.evaluation
        comparison = aggregate(evaluations, selected_unit_ids=config["units"])
        write_json(run / "comparison.json", comparison.model_dump(mode="json"))
        config["outcomes"] = outcomes
        config["comparison"] = "comparison.json"
        completed = sum(len(available) for available in evaluations.values())
        total = len(units) * len(config["units"])
        config["status"] = "completed" if completed == total and not config.get("index_failures") else "partial"
        data = json.dumps(config, ensure_ascii=False, allow_nan=False, indent=2)
        write_text(run / "configs.md", f"# Experiment configuration\n\n```json\n{data}\n```\n")
    finally:
        os.close(run_fd)
    print(f"Evaluation: {len(selected) - failures} succeeded, {failures} failed; run {config['status']}.")
    return 1 if failures or close_failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ghl-mas-evaluate", description="Evaluate an existing persisted run in place.")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--run", required=True)
    parser.add_argument("--solution")
    parser.add_argument("--unit")
    options = parser.parse_args(argv)
    try:
        _name(options.run)
        return evaluate_run(options.results_dir / options.run, options.solution, options.unit)
    except (OSError, ValueError) as error:
        print(f"Evaluation failed ({type(error).__name__}). Check the run, selectors, and saved artifacts.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
