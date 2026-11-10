"""Reserve experiments and publish their unit artifacts."""

import csv
import hashlib
import json
import os
import re
import time
import unicodedata
from collections.abc import Callable, Sequence
from datetime import datetime
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote
from zoneinfo import ZoneInfo

from evaluation.matching import SIMILARITY_THRESHOLD
from model_runtime import CallRecord
from schemas import EvaluationResult, GenerationResult, Unit, UsageRecord, generation_input, validate_cases

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
RUN_TIMEZONE = ZoneInfo("America/Recife")
SOLUTIONS = ("one-shot", "GHL", "Multiagent")
RESULT_SCHEMA_VERSION = 1

_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}")
_WINDOWS_DEVICES = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
_CSV_FIELDS = (
    "unit_id", "status", "precision", "recall", "f1", "generated_count", "reference_count",
    "match_count", "tokens_used", "generation_input_tokens", "generation_output_tokens",
    "generation_usage_status", "embedding_requests", "embedding_input_tokens",
    "embedding_output_tokens", "embedding_usage_status", "failure_stage", "failure_type",
)


def reserve_run(root: Path, now: Callable[[], datetime]) -> Path:
    """Create a new timestamp directory, sleeping to the next second on collision.

    The clock can return an aware datetime in any zone, or a local Recife datetime.
    """
    root.mkdir(parents=True, exist_ok=True)
    while True:
        instant = now()
        if instant.tzinfo is not None:
            instant = instant.astimezone(RUN_TIMEZONE)
        run = root / instant.strftime(TIMESTAMP_FORMAT)
        try:
            run.mkdir()
        except FileExistsError:
            time.sleep(1 - instant.microsecond / 1_000_000)
        else:
            return run


def write_text(path: Path, content: str) -> None:
    """Publish complete UTF-8 bytes atomically in the destination directory."""
    temporary = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix=".write-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content.encode("utf-8"))
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_json(path: Path, content: object) -> None:
    write_text(path, json.dumps(content, ensure_ascii=False, allow_nan=False, indent=2) + "\n")


def _directory(parent: Path, name: str, *, exist_ok: bool = True) -> Path:
    path = parent / name
    if path.is_symlink():
        raise ValueError("Artifact directories cannot be symbolic links")
    path.mkdir(exist_ok=exist_ok)
    return path


def _id_component(identifier: str) -> str:
    if _SAFE_ID.fullmatch(identifier) and identifier.lower() not in _WINDOWS_DEVICES | {"intermediate"}:
        return identifier
    return "~" + hashlib.sha256(identifier.encode("utf-8")).hexdigest()


def _safe_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKC", title)
    return re.sub(r"[^\w-]+", "_", normalized).strip("_-")[:48].rstrip("_-") or "untitled"


def _markdown_inline(text: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()<>#+!|])", r"\\\1", " ".join(text.split()))


def _case_files(unit_dir: Path, unit: Unit, result: GenerationResult) -> dict:
    requirements = {}
    case_paths = {}
    case_dirs = {}
    for requirement in unit.requirements:
        req_dir = _directory(unit_dir, _id_component(requirement.id))
        req_file = req_dir / "requirement.md"
        write_text(req_file, f"# {_markdown_inline(requirement.id)}\n\n{requirement.text}\n")
        requirements[requirement.id] = req_file.relative_to(unit_dir).as_posix()
        case_dirs[requirement.id] = _directory(req_dir, "test cases")

    for sequence, case in enumerate(result.cases, 1):
        filename = f"{sequence}_{_safe_title(case.title)}.md"
        links = dict.fromkeys(case.requirement_ids)
        requirements_line = ", ".join(map(_markdown_inline, links))
        text = (
            f"# {_markdown_inline(case.title)}\n\n"
            f"Case ID · {_markdown_inline(case.id)}\n\n"
            f"Requirements · {requirements_line}\n\n{case.description}\n"
        )
        paths = {}
        for requirement_id in links:
            path = case_dirs[requirement_id] / filename
            write_text(path, text)
            paths[requirement_id] = path.relative_to(unit_dir).as_posix()
        case_paths[case.id] = paths
    return {"requirements": requirements, "cases": case_paths}


def _save_intermediate(unit_dir: Path, result: GenerationResult) -> dict:
    directory = _directory(unit_dir, "intermediate")
    trace = result.trace
    if trace is None:
        return {}

    write_json(directory / "trace.json", trace)
    write_json(directory / "initial.json", trace["initial"])
    rounds = []
    for revision in trace["rounds"]:
        round_dir = _directory(directory, f"round_{revision['number']:03d}")
        attempts = []
        for position, candidate in enumerate(revision["candidates"], 1):
            path = round_dir / f"attempt_{position}.json"
            write_json(path, candidate["attempt"])
            attempts.append(path.relative_to(unit_dir).as_posix())
        decision = round_dir / "decision.json"
        write_json(decision, revision)
        rounds.append({"decision": decision.relative_to(unit_dir).as_posix(), "attempts": attempts})
    return {"trace": "intermediate/trace.json", "initial": "intermediate/initial.json", "rounds": rounds}


def _write_csv(unit_dir: Path, payload: dict, matches: dict, usage: UsageRecord, embedding_usage: UsageRecord) -> None:
    evaluation = payload["evaluation"] or {}
    tokens = None
    if usage.input_tokens is not None and usage.output_tokens is not None:
        tokens = usage.input_tokens + usage.output_tokens
    failure = payload["failure"] or {}
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=_CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerow({
        "unit_id": payload["unit_id"],
        "status": payload["status"],
        **{metric: evaluation.get(metric) for metric in ("precision", "recall", "f1")},
        "generated_count": len(payload["generated_cases"]),
        "reference_count": len(payload["reference_cases"]),
        "match_count": len(matches["matches"]) if evaluation else None,
        "tokens_used": tokens,
        "generation_input_tokens": usage.input_tokens,
        "generation_output_tokens": usage.output_tokens,
        "generation_usage_status": usage.status,
        "embedding_requests": payload["usage"]["embedding_requests"],
        "embedding_input_tokens": embedding_usage.input_tokens,
        "embedding_output_tokens": embedding_usage.output_tokens,
        "embedding_usage_status": embedding_usage.status,
        "failure_stage": failure.get("stage"),
        "failure_type": failure.get("error_type"),
    })
    write_text(unit_dir / "results.csv", stream.getvalue())


def write_solution_index(solution_dir: Path) -> None:
    """Index the unique cases from each published unit snapshot."""
    _directory(solution_dir.parent, solution_dir.name)
    lines = [f"# {_markdown_inline(solution_dir.name)} · Requirements to tests"]
    for path in sorted(solution_dir.glob("*/results.json")):
        if path.is_symlink() or path.parent.is_symlink():
            continue
        payload = json.loads(path.read_bytes())
        lines.extend(["", f"## {_markdown_inline(payload['unit_id'])}", "", f"Status · {payload['status']}"])
        for case in payload["generated_cases"]:
            links = payload["links"]["cases"][case["id"]]
            targets = ", ".join(
                f"[{_markdown_inline(req_id)}]({quote(f'{path.parent.name}/{relative}')})"
                for req_id, relative in links.items()
            )
            lines.append(f"- {_markdown_inline(case['id'])} · {_markdown_inline(case['title'])} · {targets}")
    write_text(solution_dir / "requirements_to_tests.md", "\n".join(lines) + "\n")


def save_unit(
    run: Path,
    solution: str,
    unit: Unit,
    result: GenerationResult,
    evaluation: EvaluationResult | None,
    *,
    failure: dict[str, str] | None = None,
    generation_attempts: Sequence[UsageRecord] = (),
    generation_calls: Sequence[CallRecord] = (),
    embedding_usage: UsageRecord | None = None,
    embedding_requests: int | None = None,
) -> None:
    """Publish a completed unit or a failed unit with any available partial result."""
    if solution not in SOLUTIONS:
        raise ValueError("Unknown solution directory")
    if (evaluation is None) != (failure is not None):
        raise ValueError("A unit requires either an evaluation or a failure")
    for items in (unit.requirements, unit.reference_cases, result.cases):
        if len({item.id for item in items}) != len(items):
            raise ValueError("Duplicate IDs in a unit artifact collection")
    validate_cases(generation_input(unit), result.cases)

    solution_dir = _directory(run, solution)
    unit_dir = _directory(solution_dir, _id_component(unit.id), exist_ok=False)
    intermediate = _save_intermediate(unit_dir, result)
    links = _case_files(unit_dir, unit, result)

    status = evaluation.status if evaluation is not None else "failed"
    automatic = evaluation.model_dump(mode="json") if evaluation is not None else None
    if evaluation is not None:
        embedding_usage, embedding_requests = evaluation.embedding_usage, evaluation.embedding_requests
    embedding_usage = embedding_usage if embedding_usage is not None else UsageRecord()
    matches = {
        "status": status,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "matches": automatic["matches"] if automatic is not None else [],
        "unmatched_generated_ids": automatic["unmatched_generated_ids"] if automatic is not None else None,
        "unmatched_reference_ids": automatic["unmatched_reference_ids"] if automatic is not None else None,
    }
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "solution": solution,
        "unit_id": unit.id,
        "parent_id": unit.parent_id,
        "status": status,
        "failure": failure,
        "requirements": [requirement.model_dump(mode="json") for requirement in unit.requirements],
        "generated_cases": [case.model_dump(mode="json") for case in result.cases],
        "reference_cases": [case.model_dump(mode="json") for case in unit.reference_cases],
        "evaluation": automatic,
        "generation": result.model_dump(mode="json", exclude={"cases", "trace", "usage"}),
        "usage": {
            "generation": result.usage.model_dump(mode="json"),
            "generation_attempts": [attempt.model_dump(mode="json") for attempt in generation_attempts],
            "generation_calls": [call.model_dump(mode="json") for call in generation_calls],
            "embedding": embedding_usage.model_dump(mode="json"),
            "embedding_requests": embedding_requests,
        },
        "links": links,
        "artifacts": {"semantic_matches": "semantic_matches.json", "csv": "results.csv", **intermediate},
    }
    _write_csv(unit_dir, payload, matches, result.usage, embedding_usage)
    write_json(unit_dir / "semantic_matches.json", matches)
    write_json(unit_dir / "results.json", payload)
