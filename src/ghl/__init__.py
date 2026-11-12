"""Grounded High-Level (GHL) test generation by selected design technique."""

from asyncio import CancelledError
from typing import Literal

from pydantic import BaseModel, Field

from tcg.runtime import Runtime, sum_usage
from tcg.schemas import GeneratedCase, GenerationInput, GenerationResult, UsageRecord, validate_cases


PROMPT_VERSION = "ghl-v1"


class Technique(BaseModel):
    id: str
    name: str
    rationale: str


# Compact, versioned black-box catalogue; the paper describes selection from
# requirements and strategy, while this study fixes a strategy in the selector prompt.
TECHNIQUES = (
    Technique(id="equivalence_partitioning", name="Equivalence partitioning", rationale="Partition valid and invalid input or behavior classes."),
    Technique(id="boundary_value_analysis", name="Boundary value analysis", rationale="Exercise values at, immediately within, and outside stated limits."),
    Technique(id="state_transition", name="State transition testing", rationale="Cover relevant states, events, transitions, and forbidden transitions."),
    Technique(id="decision_table", name="Decision table testing", rationale="Cover combinations of conditions and their resulting actions."),
    Technique(id="combinatorial", name="Combinatorial testing", rationale="Cover meaningful combinations of multiple requirement factors."),
    Technique(id="use_case", name="Use-case / user-flow testing", rationale="Adaptation: cover an end-to-end user goal where requirements describe a workflow."),
    Technique(id="error_guessing", name="Error guessing", rationale="Adaptation: explore plausible misuse and failure conditions grounded in requirements."),
)


class TechniqueChoice(BaseModel):
    technique_id: str
    rationale: str = Field(min_length=1)


class _Selection(BaseModel):
    selections: list[TechniqueChoice]


class _CaseBatch(BaseModel):
    cases: list[GeneratedCase]


class GHLFailure(ValueError):
    """A technique call failed after the selection was validated."""

    def __init__(
        self, stage: str, error_type: str, partial_result: GenerationResult, *, detail: str | None = None,
    ):
        super().__init__(detail or f"GHL {stage} failed ({error_type})")
        self.stage = stage
        self.error_type = error_type
        self.partial_result = partial_result


def _result(collected: list[GeneratedCase], selection: _Selection, usage: list[UsageRecord]) -> GenerationResult:
    # Dedup only exact title+description matches; no normalization or fuzzy merging.
    consolidated: list[GeneratedCase] = []
    by_text: dict[tuple[str, str], int] = {}
    for case in collected:
        key = (case.title, case.description)
        if key in by_text:
            index = by_text[key]
            prior = consolidated[index]
            links = list(dict.fromkeys([*prior.requirement_ids, *case.requirement_ids]))
            consolidated[index] = prior.model_copy(update={"requirement_ids": links})
        else:
            by_text[key] = len(consolidated)
            consolidated.append(case)
    stable_cases = [case.model_copy(update={"id": f"G-{index:03d}"}) for index, case in enumerate(consolidated, 1)]
    return GenerationResult(
        cases=stable_cases,
        usage=sum_usage(usage),
        selected_techniques=[choice.technique_id for choice in selection.selections],
        technique_rationales={choice.technique_id: choice.rationale for choice in selection.selections},
        prompt_version=PROMPT_VERSION,
    )


async def generate_ghl(
    input: GenerationInput,
    runtime: Runtime,
    *,
    output_mode: Literal["batch", "per_requirement", "per_case"] = "batch",
) -> GenerationResult:
    """Select techniques once; generate per technique, optionally per requirement."""
    if output_mode not in {"batch", "per_requirement", "per_case"}:
        raise ValueError(f"Unsupported GHL output mode: {output_mode}")
    usage_start = len(runtime.usage_records)
    catalogue = [technique.model_dump() for technique in TECHNIQUES]
    selection = await runtime.run(
        "ghl_select_techniques",
        "Select only useful test design techniques from the supplied catalogue based on all requirements. "
        "Consider this fixed test strategy: cover normal and abnormal behavior, important input partitions, "
        "stated limits, states and transitions, condition combinations, user flows, and plausible failures. "
        "Return a rationale for every selection; return an empty selection if none apply.",
        input,
        _Selection,
        extra={"catalogue_version": "ghl-techniques-v1", "catalogue": catalogue, "prompt_version": PROMPT_VERSION},
    )
    known = {technique.id for technique in TECHNIQUES}
    selected_ids = [choice.technique_id for choice in selection.selections]
    invalid = set(selected_ids) - known
    if invalid:
        raise ValueError("Unknown GHL technique IDs: " + ", ".join(sorted(invalid)))
    if len(set(selected_ids)) != len(selected_ids):
        raise ValueError("GHL technique selection contains duplicate IDs")

    collected: list[GeneratedCase] = []
    for choice in selection.selections:
        technique = next(item for item in TECHNIQUES if item.id == choice.technique_id)
        stage = f"ghl_generate_{technique.id}"
        scopes = input.requirements if output_mode in {"per_requirement", "per_case"} else [None]
        for requirement in scopes:
            target = requirement.id if requirement is not None else technique.id
            answer = None
            try:
                answer = await runtime.run(
                    stage,
                    f"Generate high-level test cases using {technique.name}. {technique.rationale} "
                    "Use all requirements supplied in context, include normal and abnormal cases, and cite only supplied IDs.",
                    input,
                    _CaseBatch,
                    extra={
                        "output_mode": output_mode,
                        "target": target,
                        "technique_id": technique.id,
                        "prompt_version": PROMPT_VERSION,
                    },
                )
                validate_cases(input, answer.cases)
                if requirement is not None:
                    for case in answer.cases:
                        if requirement.id not in case.requirement_ids:
                            raise ValueError(
                                f"GHL case {case.id!r} generated for {requirement.id!r} "
                                "does not link to its scoped requirement"
                            )
                if output_mode == "per_case" and len(answer.cases) > 1:
                    raise ValueError("GHL per_case output returned more than one case for a call")
            except CancelledError as error:
                error.tcg_partial = (stage, _result(collected, selection, runtime.usage_records[usage_start:]))
                raise
            except Exception as error:
                # Preserve local validation diagnostics for direct callers and
                # keep raw runtime exceptions outside the partial result.
                detail = str(error) if answer is not None and isinstance(error, ValueError) else None
                failure = GHLFailure(
                    stage, type(error).__name__, _result(collected, selection, runtime.usage_records[usage_start:]),
                    detail=detail,
                )
            else:
                collected.extend(answer.cases)
                continue
            raise failure

    return _result(collected, selection, runtime.usage_records[usage_start:])
