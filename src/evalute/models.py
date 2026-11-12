"""Evaluation-only contracts. The generator never imports this package."""

from typing import Literal

from pydantic import BaseModel, Field, NonNegativeInt

from src.tcg.schemas import GeneratedCase, Identifier, Unit, UsageRecord


class ReferenceCase(GeneratedCase):
    source: str
    link_method: str
    link_status: str
    secondary_domains: list[str] = Field(default_factory=list)


class EvaluationUnit(Unit):
    reference_cases: list[ReferenceCase] = Field(default_factory=list)
    parent_id: Identifier | None = None


class SemanticMatch(BaseModel):
    generated_id: Identifier
    reference_id: Identifier
    similarity: float


class EvaluationResult(BaseModel):
    status: Literal["evaluated", "not_evaluable"]
    generated_count: NonNegativeInt
    reference_count: NonNegativeInt = 0
    matches: list[SemanticMatch] = Field(default_factory=list)
    unmatched_generated_ids: list[Identifier] = Field(default_factory=list)
    unmatched_reference_ids: list[Identifier] = Field(default_factory=list)
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    embedding_usage: UsageRecord = Field(default_factory=UsageRecord)
    embedding_requests: NonNegativeInt | None = None
