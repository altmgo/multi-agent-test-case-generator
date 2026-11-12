"""Write the v1 report format without rewriting generation artifacts."""

import csv
from io import StringIO
from pathlib import Path

from src.tcg.output import write_json, write_text
from src.tcg.schemas import UsageRecord

from .matching import SIMILARITY_THRESHOLD
from .models import EvaluationResult
from .reader import GeneratedUnit

_CSV_FIELDS = (
    "unit_id", "status", "precision", "recall", "f1", "generated_count", "reference_count",
    "match_count", "tokens_used", "generation_input_tokens", "generation_output_tokens",
    "generation_usage_status", "embedding_requests", "embedding_input_tokens",
    "embedding_output_tokens", "embedding_usage_status", "failure_stage", "failure_type",
)


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


def publish_unit(
    unit: GeneratedUnit,
    model: str,
    evaluation: EvaluationResult | None,
    failure: dict[str, str] | None,
    embedding_usage: UsageRecord,
    embedding_requests: int | None,
) -> None:
    automatic = evaluation.model_dump(mode="json") if evaluation is not None else None
    status = evaluation.status if evaluation is not None else "failed"
    if evaluation is not None:
        embedding_usage, embedding_requests = evaluation.embedding_usage, evaluation.embedding_requests
    matches = {
        "status": status,
        "embedding_model": model,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "matches": automatic["matches"] if automatic is not None else [],
        "unmatched_generated_ids": automatic["unmatched_generated_ids"] if automatic is not None else None,
        "unmatched_reference_ids": automatic["unmatched_reference_ids"] if automatic is not None else None,
    }
    payload = {
        "schema_version": 1,
        "solution": unit.solution,
        "unit_id": unit.dataset.id,
        "parent_id": unit.dataset.parent_id,
        "status": status,
        "failure": failure,
        "embedding_model": model,
        "requirements": [requirement.model_dump(mode="json") for requirement in unit.dataset.requirements],
        "generated_cases": [case.model_dump(mode="json") for case in unit.cases],
        "reference_cases": [case.model_dump(mode="json") for case in unit.dataset.reference_cases],
        "evaluation": automatic,
        "generation": unit.generation,
        "usage": {
            "generation": unit.usage.model_dump(mode="json"),
            "generation_attempts": [],
            "generation_calls": [],
            "embedding": embedding_usage.model_dump(mode="json"),
            "embedding_requests": embedding_requests,
        },
        "links": unit.links,
        "artifacts": {"semantic_matches": "semantic_matches.json", "csv": "results.csv", **unit.intermediate},
    }
    _write_csv(unit.path, payload, matches, unit.usage, embedding_usage)
    write_json(unit.path / "semantic_matches.json", matches)
    write_json(unit.path / "results.json", payload)
