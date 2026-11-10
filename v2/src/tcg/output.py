"""Write the generation artifacts in the original Markdown layout."""

import hashlib
import json
import os
import re
import time
import unicodedata
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote
from zoneinfo import ZoneInfo

from .schemas import GenerationResult, Unit, generation_input, validate_cases

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
RUN_TIMEZONE = ZoneInfo("America/Recife")
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}")
_WINDOWS_DEVICES = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}


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


def save_unit(solution_dir: Path, unit: Unit, result: GenerationResult, status: str) -> list[str]:
    validate_cases(generation_input(unit), result.cases)
    if len({case.id for case in result.cases}) != len(result.cases):
        raise ValueError("Generated case IDs must be unique")
    unit_dir = _directory(solution_dir, _id_component(unit.id))
    links = _case_files(unit_dir, unit, result)
    if result.trace is not None:
        _save_intermediate(unit_dir, result)

    lines = ["", f"## {_markdown_inline(unit.id)}", "", f"Status · {status}"]
    for case in result.cases:
        targets = ", ".join(
            f"[{_markdown_inline(req_id)}]({quote(f'{unit_dir.name}/{relative}')})"
            for req_id, relative in links["cases"][case.id].items()
        )
        lines.append(f"- {_markdown_inline(case.id)} · {_markdown_inline(case.title)} · {targets}")
    return lines
