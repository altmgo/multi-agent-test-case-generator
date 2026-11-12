"""Read requirement units from the normalized dataset directory."""

import re
from pathlib import Path

from .schemas import Unit

DATASETS = ("firefox", "e2edev")
_FILENAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}\.json")


def _read_unit(directory: Path, filename: str) -> Unit:
    if not _FILENAME.fullmatch(filename):
        raise ValueError(f"Use the normalized filename including .json: {filename!r}")
    path = directory / filename
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Normalized unit not found as a regular file: {filename}")
    unit = Unit.model_validate_json(path.read_bytes())
    if unit.id != path.stem:
        raise ValueError(f"Normalized unit ID does not match filename: {filename}")
    if len({requirement.id for requirement in unit.requirements}) != len(unit.requirements):
        raise ValueError(f"Duplicate requirement IDs in {filename}")
    return unit


def select_units(directory: Path, filenames: list[str], datasets: list[str]) -> list[Unit]:
    selected: dict[str, Unit] = {}
    for filename in dict.fromkeys(filenames):
        unit = _read_unit(directory, filename)
        if not unit.generatable:
            raise ValueError(f"Normalized unit is archival: {filename}")
        selected[filename] = unit

    if datasets or not filenames:
        patterns = [f"{name}_*.json" for name in dict.fromkeys(datasets)] if datasets else ["*.json"]
        for pattern in patterns:
            for path in sorted(directory.glob(pattern)):
                if path.name not in selected:
                    unit = _read_unit(directory, path.name)
                    if unit.generatable:
                        selected[path.name] = unit

    if not selected:
        raise ValueError(f"No eligible normalized units found in {directory}")
    return list(selected.values())
