"""Review saved automatic matches without calling any model."""

import argparse
import fcntl
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from random import Random

from pydantic import BaseModel

import persistence
from evaluation.metrics import scores
from schemas import EvaluationResult, GeneratedCase, HumanDecision, HumanEvaluation, ReferenceCase, Requirement


class _AutomaticUnit(BaseModel):
    evaluation: EvaluationResult
    requirements: list[Requirement]
    generated_cases: list[GeneratedCase]
    reference_cases: list[ReferenceCase]


@dataclass(frozen=True)
class _Pair:
    generated: GeneratedCase
    reference: ReferenceCase
    requirements: list[Requirement]

    @property
    def ids(self) -> tuple[str, str]:
        return self.generated.id, self.reference.id


@dataclass(frozen=True)
class _Review:
    path: Path
    original: bytes
    payload: dict
    evaluation: EvaluationResult
    pairs: list[_Pair]


def _finalized(payload: object) -> bool:
    return (
        isinstance(payload, dict)
        and payload.get("schema_version") == persistence.RESULT_SCHEMA_VERSION
        and payload.get("status") in ("evaluated", "not_evaluable")
        and isinstance(payload.get("evaluation"), dict)
        and isinstance(payload["evaluation"].get("matches"), list)
    )


def _load(path: Path) -> _Review:
    path = path.resolve(strict=True)
    original = path.read_bytes()
    payload = json.loads(original)
    if not _finalized(payload):
        raise ValueError("The unit has no finalized automatic evaluation in the supported format")

    unit = _AutomaticUnit.model_validate(payload)
    automatic = unit.evaluation
    requirements = {requirement.id: requirement for requirement in unit.requirements}
    generated = {case.id: case for case in unit.generated_cases}
    references = {case.id: case for case in unit.reference_cases}
    if (
        len(requirements) != len(unit.requirements)
        or len(generated) != len(unit.generated_cases)
        or len(references) != len(unit.reference_cases)
        or automatic.generated_count != len(generated)
        or automatic.reference_count != len(references)
        or automatic.status != payload["status"]
        or (automatic.status == "evaluated") != bool(references)
    ):
        raise ValueError("Inconsistent automatic evaluation or unit snapshots")

    pairs = []
    matched_generated = set()
    matched_references = set()
    for match in automatic.matches:
        if match.generated_id in matched_generated or match.reference_id in matched_references:
            raise ValueError("Automatic matches must be one-to-one")
        matched_generated.add(match.generated_id)
        matched_references.add(match.reference_id)

        generated_case = generated.get(match.generated_id)
        reference_case = references.get(match.reference_id)
        if generated_case is None or reference_case is None:
            raise ValueError("An automatic match refers to a missing case")
        linked_ids = set(generated_case.requirement_ids) | set(reference_case.requirement_ids)
        if not linked_ids <= requirements.keys():
            raise ValueError("An automatic match refers to a missing requirement")
        pairs.append(_Pair(generated_case, reference_case, [
            requirement for requirement in unit.requirements if requirement.id in linked_ids
        ]))

    pairs.sort(key=lambda pair: pair.ids)
    Random(0).shuffle(pairs)
    return _Review(path, original, payload, automatic, pairs)


def _save(review: _Review, decisions: list[HumanDecision]) -> HumanEvaluation:
    by_pair = {(decision.generated_id, decision.reference_id): decision for decision in decisions}
    if len(by_pair) != len(decisions) or by_pair.keys() != {pair.ids for pair in review.pairs}:
        raise ValueError("Submit exactly one decision for each automatic match")

    ordered = [HumanDecision.model_validate(by_pair[pair.ids].model_dump()) for pair in review.pairs]
    counts = Counter(decision.verdict for decision in ordered)
    generated = review.evaluation.generated_count
    references = review.evaluation.reference_count
    result = HumanEvaluation(
        generated_count=generated,
        reference_count=references,
        decisions=ordered,
        equivalent_count=counts["equivalent"],
        different_count=counts["different"],
        inconclusive_count=counts["inconclusive"],
        **scores(counts["equivalent"], generated, references),
    )

    payload = dict(review.payload)
    if (previous := payload.get("human_evaluation")) is not None:
        payload["human_evaluation_history"] = [*payload.get("human_evaluation_history", []), previous]
    payload["human_evaluation"] = result.model_dump(mode="json")

    # Serialize writers, and reject a review based on a superseded snapshot.
    directory_fd = os.open(review.path.parent, os.O_RDONLY)
    try:
        try:
            fcntl.flock(directory_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("Another review is being saved for this unit") from error
        if review.path.read_bytes() != review.original:
            raise ValueError("The result changed during review. Open it again to review the latest version.")
        persistence.write_json(review.path, payload)
    finally:
        os.close(directory_fd)
    return result


def review_unit(path: Path, decisions: list[HumanDecision]) -> HumanEvaluation:
    """Commit a complete decision set for a unit's finalized automatic matches."""
    return _save(_load(path), decisions)


class _Cancelled(Exception):
    pass


def _choose(label: str, options: list[str], requested: str | None) -> str:
    if not options:
        raise ValueError(f"No reviewable {label.lower()} available")
    if requested is not None:
        if requested in options:
            return requested
        raise ValueError(f"Unknown or unavailable {label.lower()}")
    numbered = {str(number): option for number, option in enumerate(options, 1)}
    for number, option in numbered.items():
        print(f"  {number}. {option}")
    while True:
        answer = input(f"{label} number (q to cancel) > ").strip().lower()
        if answer == "q":
            raise _Cancelled
        if answer in numbered:
            return numbered[answer]
        print("Choose one of the listed numbers.")


def _reviewable_unit_id(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_bytes())
    except (OSError, ValueError):
        return None
    if _finalized(payload) and isinstance(payload.get("unit_id"), str):
        return payload["unit_id"]
    return None


def _select(args: argparse.Namespace) -> Path:
    by_run: dict[str, list[Path]] = {}
    for path in sorted(args.results_dir.glob("*/*/*/results.json")):
        if path.parents[1].name in persistence.SOLUTIONS:
            by_run.setdefault(path.parents[2].name, []).append(path)
    run_names = sorted(by_run, reverse=True)
    if args.run is None:
        run_names = [name for name in run_names if any(_reviewable_unit_id(path) for path in by_run[name])]
    run = _choose("Run", run_names, args.run)
    by_solution = {name: {} for name in persistence.SOLUTIONS}
    for path in by_run[run]:
        unit_id = _reviewable_unit_id(path)
        if unit_id is None:
            continue
        units = by_solution[path.parents[1].name]
        if unit_id in units:
            raise ValueError("Duplicate unit ID in one solution")
        units[unit_id] = path
    solutions = {name.casefold(): name for name, units in by_solution.items() if units}
    requested_solution = args.solution.casefold() if args.solution is not None else None
    solution = _choose(
        "Solution", list(solutions.values()), solutions.get(requested_solution, args.solution)
    )
    units = by_solution[solution]
    return units[_choose("Unit", sorted(units), args.unit)]


def _confirm(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [y/N] > ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"", "n", "no", "q"}:
            return False
        print("Enter y to confirm or n to cancel.")


def _show_case(label: str, case: GeneratedCase | ReferenceCase) -> None:
    print(f"\n{label}")
    if case.title and case.title.strip() != case.id:
        print(case.title)
    print(case.description)


def _judge(pair: _Pair, number: int, total: int) -> HumanDecision:
    print(f"\nPair {number} of {total}\nRequirements")
    for requirement in pair.requirements:
        print(f"- {requirement.text}")
    _show_case("Reference", pair.reference)
    _show_case("Generated", pair.generated)
    while True:
        verdict = input("Verdict (equivalent, different, inconclusive, or q to cancel) > ").strip().lower()
        if verdict == "q":
            raise _Cancelled
        if verdict in {"equivalent", "different", "inconclusive"}:
            break
        print("Enter equivalent, different, or inconclusive.")
    justification = input("Justification (optional) > ").strip()
    return HumanDecision(generated_id=pair.generated.id, reference_id=pair.reference.id,
                         verdict=verdict, justification=justification)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ghl-mas-review", description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--run", help="Run directory name")
    parser.add_argument("--solution", help="Solution name")
    parser.add_argument("--unit", help="Unit ID")
    args = parser.parse_args(argv)
    try:
        review = _load(_select(args))
        if review.payload.get("human_evaluation") is not None and not _confirm(
            "A review already exists. Start a new review?"
        ):
            raise _Cancelled

        if not review.pairs:
            message = "No automatic matches." if review.evaluation.reference_count else "No reference cases."
            print(message)
        decisions = [_judge(pair, number, len(review.pairs)) for number, pair in enumerate(review.pairs, 1)]
        if not _confirm("Save this review?"):
            raise _Cancelled
        _save(review, decisions)
    except (_Cancelled, EOFError, KeyboardInterrupt):
        print("\nReview cancelled.")
        return 0
    except (OSError, ValueError) as error:
        print(f"Review error: {error}", file=sys.stderr)
        return 1
    print("Review saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
