"""Per-unit semantic evaluation and common-unit comparisons."""

from collections.abc import Iterable, Mapping

import numpy as np
from pydantic import BaseModel, NonNegativeInt

from datasets.firefox import ARCHIVE_ID as FIREFOX_ARCHIVE_ID
from schemas import EvaluationResult, GeneratedCase, SemanticMatch, Unit, UsageRecord

from .embeddings import Embedder, canonical_text, vector_matrix
from .matching import match


def scores(pairs: int, generated: int, references: int) -> dict[str, float | None]:
    """Score credited pairs using the complete generated and reference sets."""
    if not references:
        return dict(precision=None, recall=None, f1=None)
    return dict(
        precision=pairs / generated if generated else 0.0,
        recall=pairs / references,
        f1=2 * pairs / (generated + references),
    )


def evaluate(unit: Unit, generated: list[GeneratedCase], embedder: Embedder) -> EvaluationResult:
    """Evaluate one unit using the same semantic instruction on both sides."""
    references = unit.reference_cases
    matched: list[tuple[int, int, float]] = []
    embedding_usage = UsageRecord(input_tokens=0, output_tokens=0)
    embedding_requests = 0
    if generated and references:
        texts = [canonical_text(case.title, case.description) for case in generated]
        for case in references:
            title = case.title
            if unit.parent_id == FIREFOX_ARCHIVE_ID and title.strip() == case.id:
                title = ""
            texts.append(canonical_text(title, case.description))

        batch = embedder.embed(texts)
        vectors = vector_matrix(batch, len(texts))
        # Scale each row before its norm to avoid overflow or underflow even
        # for very large or small finite coordinates.
        _, exponents = np.frexp(np.abs(vectors).max(axis=1, keepdims=True))
        vectors = np.ldexp(vectors, -exponents)
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        matched = match(vectors[:len(generated)] @ vectors[len(generated):].T)
        embedding_usage = batch.usage
        embedding_requests = batch.request_count

    matched_generated = {row for row, _, _ in matched}
    matched_references = {column for _, column, _ in matched}
    return EvaluationResult(
        status="evaluated" if references else "not_evaluable",
        generated_count=len(generated),
        reference_count=len(references),
        matches=[
            SemanticMatch(generated_id=generated[row].id, reference_id=references[column].id, similarity=score)
            for row, column, score in matched
        ],
        unmatched_generated_ids=[case.id for row, case in enumerate(generated) if row not in matched_generated],
        unmatched_reference_ids=[case.id for column, case in enumerate(references) if column not in matched_references],
        embedding_usage=embedding_usage,
        embedding_requests=embedding_requests,
        **scores(len(matched), len(generated), len(references)),
    )


class AggregateMetrics(BaseModel):
    generated_count: NonNegativeInt
    reference_count: NonNegativeInt
    match_count: NonNegativeInt
    precision: float | None
    recall: float | None
    f1: float | None


class ComparisonResult(BaseModel):
    unit_ids: list[str]
    total_unit_ids: list[str]
    evaluable_unit_ids: dict[str, list[str]]
    coverage: float | None
    metrics: dict[str, AggregateMetrics]


def aggregate(
    results: Mapping[str, Mapping[str, EvaluationResult]], *, selected_unit_ids: Iterable[str] = ()
) -> ComparisonResult:
    """Micro-average each solution on the shared evaluated subset."""
    total_units = set(selected_unit_ids)
    evaluable = {}
    for solution, units in results.items():
        total_units.update(units)
        evaluable[solution] = {
            unit_id for unit_id, result in units.items() if result.status == "evaluated"
        }
    common = sorted(set.intersection(*evaluable.values())) if evaluable else []
    metrics = {}
    for solution, units in results.items():
        generated_count = sum(units[unit_id].generated_count for unit_id in common)
        reference_count = sum(units[unit_id].reference_count for unit_id in common)
        match_count = sum(len(units[unit_id].matches) for unit_id in common)
        metrics[solution] = AggregateMetrics(
            generated_count=generated_count,
            reference_count=reference_count,
            match_count=match_count,
            **scores(match_count, generated_count, reference_count),
        )
    return ComparisonResult(
        unit_ids=common,
        total_unit_ids=sorted(total_units),
        evaluable_unit_ids={solution: sorted(unit_ids) for solution, unit_ids in evaluable.items()},
        coverage=len(common) / len(total_units) if total_units else None,
        metrics=metrics,
    )
