"""Data contracts for normalized datasets and generation."""
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    NonNegativeInt,
    StringConstraints,
    model_validator,
)

Identifier = Annotated[str, StringConstraints(pattern=r"\S")]


class Requirement(BaseModel):
    id: Identifier
    text: str
    language: str
    source: str


class _LinkedCase(BaseModel):
    id: Identifier
    title: str
    description: str
    requirement_ids: list[Identifier] = Field(min_length=1)


class GeneratedCase(_LinkedCase):
    pass


class Unit(BaseModel):
    # Normalized files also carry evaluation references. Drop them at ingestion.
    model_config = ConfigDict(extra="ignore")

    id: Identifier
    requirements: list[Requirement]
    generatable: bool = True


class GenerationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit_id: Identifier
    requirements: list[Requirement]


def generation_input(unit: Unit) -> GenerationInput:
    """Select the fields a generator may receive from an eligible unit."""
    if not unit.generatable:
        raise ValueError(f"Unit {unit.id!r} is not eligible for generation")
    return GenerationInput(unit_id=unit.id, requirements=unit.requirements)


def validate_cases(input: GenerationInput, cases: list[GeneratedCase]) -> None:
    """Reject generated cases that link outside the unit."""
    requirement_ids = {requirement.id for requirement in input.requirements}
    for case in cases:
        if not case.requirement_ids:
            raise ValueError(f"Case {case.id!r} must link to a requirement")
        unknown_ids = set(case.requirement_ids) - requirement_ids
        if unknown_ids:
            raise ValueError(
                f"Case {case.id!r} links to unknown requirement IDs: "
                + ", ".join(sorted(unknown_ids))
            )


class UsageRecord(BaseModel):
    input_tokens: NonNegativeInt | None = None
    output_tokens: NonNegativeInt | None = None
    details: dict[str, NonNegativeInt] | None = None
    status: Literal["available", "partial", "unavailable"] = "unavailable"

    @model_validator(mode="after")
    def set_availability(self) -> Self:
        if self.input_tokens is not None and self.output_tokens is not None:
            self.status = "available"
        elif self.input_tokens is not None or self.output_tokens is not None or self.details:
            self.status = "partial"
        else:
            self.status = "unavailable"
        return self


class GenerationResult(BaseModel):
    cases: list[GeneratedCase]
    usage: UsageRecord = Field(default_factory=UsageRecord)
    selected_techniques: list[str] = Field(default_factory=list)
    technique_rationales: dict[str, str] = Field(default_factory=dict)
    prompt_version: str | None = None
    trace: dict[str, JsonValue] | None = None


class AgentOpinion(BaseModel):
    agent: str
    feedback: str
    request_revision: bool = False
    confirmed_blockers: list[str] = Field(default_factory=list)
    blocker_assessment_complete: bool = True


class CandidateAssessment(BaseModel):
    candidate_id: Identifier
    cases: list[GeneratedCase]
    opinions: list[AgentOpinion] = Field(default_factory=list)
    valid: bool = True
    confirmed_blockers: NonNegativeInt = 0
    covered_requirements: NonNegativeInt = 0
    duplicates: NonNegativeInt = 0
    comparable: bool = Field(default=True, description="Whether the confirmed blocker count is complete")


