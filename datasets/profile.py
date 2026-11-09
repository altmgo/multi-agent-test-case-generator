"""Describe reference coverage and isolate calibration statistics from unit data."""

import csv
import json
from collections import Counter
from io import StringIO
from pathlib import Path
from statistics import quantiles

from schemas import Unit

from ._publication import publish

PROFILE_VERSION = 1


def _index_units(units: list[Unit]) -> dict[str, Unit]:
    indexed = {}
    for unit in units:
        if unit.id in indexed:
            raise ValueError(f"Duplicate unit ID: {unit.id!r}")
        indexed[unit.id] = unit
    return indexed


def _requirement_counts(unit: Unit) -> dict[str, int]:
    linked_counts: Counter[str] = Counter()
    for case in unit.reference_cases:
        linked_counts.update(set(case.requirement_ids))
    return {requirement.id: linked_counts[requirement.id] for requirement in unit.requirements}


def _aggregate(counts: list[int]) -> dict:
    """Use inclusive linear interpolation at ranks (n - 1) * (0.25, 0.5, 0.75)."""
    if len(counts) > 1:
        q1, median, q3 = quantiles(counts, n=4, method="inclusive")
    elif counts:
        q1 = median = q3 = float(counts[0])
    else:
        q1 = median = q3 = None

    histogram = Counter(counts)
    return {
        "requirement_count": len(counts),
        "histogram": {str(count): histogram[count] for count in sorted(histogram)},
        "quartiles": {"q1": q1, "median": median, "q3": q3},
    }


def coverage_profile(units: list[Unit]) -> dict:
    """Return local coverage with one row per requirement, including zeros.

    The histogram contains observed bins only. Quartiles are null for an
    empty corpus.
    """
    indexed = _index_units(units)
    table = [
        {"unit_id": unit_id, "requirement_id": requirement_id, "scenario_count": count}
        for unit_id, unit in sorted(indexed.items())
        for requirement_id, count in sorted(_requirement_counts(unit).items())
    ]
    return {"table": table, "aggregate": _aggregate([row["scenario_count"] for row in table])}


def calibration_profile(
    units: list[Unit], calibration_ids: set[str], evaluated_ids: set[str]
) -> dict:
    """Return aggregate statistics for an explicit sample disjoint from evaluation."""
    if not calibration_ids:
        raise ValueError("Select at least one calibration unit")
    overlap = calibration_ids & evaluated_ids
    if overlap:
        raise ValueError("Calibration and evaluated unit IDs overlap: " + ", ".join(sorted(overlap)))

    indexed = _index_units(units)
    for label, selected in (("calibration", calibration_ids), ("evaluated", evaluated_ids)):
        unknown = selected - indexed.keys()
        if unknown:
            raise ValueError(f"Unknown {label} unit IDs: " + ", ".join(sorted(unknown)))

    counts = [
        count
        for unit_id in calibration_ids
        for count in _requirement_counts(indexed[unit_id]).values()
    ]
    if not counts:
        raise ValueError("Calibration units must contain at least one requirement")
    return _aggregate(counts)


def _json_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def save_coverage_profile(units: list[Unit], output: Path, *, dataset_version: str) -> None:
    """Publish a versioned descriptive JSON summary and two local CSV files."""
    if output.suffix != ".json":
        raise ValueError("Coverage profile output must be a JSON file")

    profile = coverage_profile(units)
    table_csv = StringIO(newline="")
    writer = csv.DictWriter(
        table_csv, fieldnames=["unit_id", "requirement_id", "scenario_count"], lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(profile["table"])

    histogram_csv = StringIO(newline="")
    histogram_writer = csv.writer(histogram_csv, lineterminator="\n")
    histogram_writer.writerow(["scenario_count", "requirement_count"])
    histogram_writer.writerows(profile["aggregate"]["histogram"].items())

    summary = {
        "profile_version": PROFILE_VERSION,
        "dataset_version": dataset_version,
        "scope": "descriptive",
        "unit_ids": sorted(unit.id for unit in units),
        "aggregate": profile["aggregate"],
    }
    publish(
        output.parent,
        {
            Path(output.with_suffix(".csv").name): table_csv.getvalue().encode("utf-8"),
            Path(output.with_suffix(".histogram.csv").name): histogram_csv.getvalue().encode("utf-8"),
            Path(output.name): _json_bytes(summary),
        },
        dataset="Descriptive coverage profile",
    )


def save_calibration_profile(
    units: list[Unit],
    calibration_ids: set[str],
    evaluated_ids: set[str],
    output: Path,
    *,
    dataset_version: str,
) -> None:
    """Publish the model payload separately from the version and selection IDs."""
    aggregate = calibration_profile(units, calibration_ids, evaluated_ids)
    provenance = {
        "profile_version": PROFILE_VERSION,
        "dataset_version": dataset_version,
        "scope": "calibration",
        "unit_ids": sorted(calibration_ids),
        "evaluated_unit_ids": sorted(evaluated_ids),
    }
    publish(
        output.parent,
        {
            Path(output.name): _json_bytes(aggregate),
            Path(output.with_suffix(".provenance.json").name): _json_bytes(provenance),
        },
        dataset="Calibration profile",
    )
