"""Evaluate an existing TCG run against normalized reference cases."""

import argparse
import sys
from pathlib import Path

from dotenv import dotenv_values

from src.tcg.output import write_json
from src.tcg.schemas import UsageRecord

from .embeddings import EMBEDDING_MODELS, EmbeddingError, EmbeddingQuotaStop, GeminiEmbedder
from .matching import SIMILARITY_THRESHOLD
from .metrics import aggregate, evaluate
from .reader import read_config, read_generated_unit
from .reports import publish_unit


def _run(options: argparse.Namespace) -> int:
    run = options.results_dir
    config = read_config(run)
    evaluations = {solution: {} for solution in config["solutions"]}
    units = [
        read_generated_unit(run, options.data_dir, solution, unit_id, outcome)
        for solution in evaluations
        for unit_id, outcome in config["outcomes"].get(solution, {}).items()
    ]
    if not units:
        raise ValueError("No generated unit artifacts in the selected TCG run")
    destination = run / "comparison.json"
    if destination.is_symlink() or (destination.exists() and not destination.is_file()):
        raise ValueError(f"Invalid result destination: {destination}")

    api_key = (dotenv_values(Path(".env"), interpolate=False).get("GOOGLE_API_KEY") or "").strip()
    if not api_key and any(unit.failure is None and unit.cases and unit.dataset.reference_cases for unit in units):
        raise ValueError("Set GOOGLE_API_KEY in .env")
    embedder = GeminiEmbedder(model=options.embedding_model, api_key=api_key)
    failed = 0
    stop_reason = None
    try:
        for unit in units:
            evaluation = None
            usage = UsageRecord(input_tokens=0, output_tokens=0)
            requests = 0
            failure = unit.failure
            if failure is None:
                try:
                    evaluation = evaluate(unit.dataset, unit.cases, embedder)
                except EmbeddingError as error:
                    usage, requests = error.usage, error.request_count
                    failure = {"stage": "evaluation", "error_type": type(error).__name__}
                    print(f"{unit.solution}/{unit.dataset.id}: {error}", file=sys.stderr, flush=True)
                    if isinstance(error, EmbeddingQuotaStop):
                        stop_reason = str(error)
                else:
                    evaluations[unit.solution][unit.dataset.id] = evaluation
            publish_unit(unit, options.embedding_model, evaluation, failure, usage, requests)
            if failure:
                failed += 1
                print(f"{unit.solution}/{unit.dataset.id}: {failure['stage']} failed ({failure['error_type']})",
                      file=sys.stderr)
            if stop_reason is not None:
                print("Embedding quota prevents continuing; writing partial results.", file=sys.stderr, flush=True)
                break
    finally:
        embedder.close()

    comparison = aggregate(evaluations, selected_unit_ids=config["units"]).model_dump(mode="json")
    write_json(destination, {
        **comparison,
        "embedding_model": options.embedding_model,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "status": "partial" if failed else "completed",
        "stop_reason": stop_reason,
    })
    print(f"Results: {destination}")
    return int(bool(failed))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evalute", description=__doc__)
    parser.add_argument("--results-dir", type=Path, required=True, help="One TCG run directory containing configs.md.")
    parser.add_argument("--embedding-model", choices=EMBEDDING_MODELS, required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("data/normalized"), help="Normalized datasets with references.")
    options = parser.parse_args(argv)
    try:
        return _run(options)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"evalute: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
