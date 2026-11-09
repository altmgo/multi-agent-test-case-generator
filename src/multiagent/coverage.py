"""Advisory coverage with a typed, aggregate-only calibration boundary."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, StringConstraints

from .state import Attempt, CoverageReport, StageRunner

HistogramBin = Annotated[str, StringConstraints(pattern=r"^(0|[1-9][0-9]*)$")]
Quartile = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class CalibrationQuartiles(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")

    q1: Quartile
    median: Quartile
    q3: Quartile


class E2EDevCalibrationProfile(BaseModel):
    """Aggregate from calibration units disjoint from the evaluated units."""

    model_config = ConfigDict(extra="forbid", revalidate_instances="always")

    requirement_count: Annotated[int, Field(gt=0)]
    histogram: dict[HistogramBin, NonNegativeInt]
    quartiles: CalibrationQuartiles


async def review_coverage(
    runner: StageRunner,
    accepted: Attempt,
    attempts: list[Attempt],
    calibration_profile: E2EDevCalibrationProfile | None,
) -> CoverageReport:
    index: dict[str, list[dict]] = {"accepted": [], "rejected": []}
    for attempt in attempts:
        assessment = attempt.assessment
        status = "accepted" if attempt is accepted else "rejected"
        index[status].extend(
            {"candidate_id": assessment.candidate_id, **case.model_dump(mode="json")}
            for case in assessment.cases
        )
    extra = {"case_index": index}
    if calibration_profile is not None:
        extra["calibration_profile"] = calibration_profile.model_dump(mode="json")
    return await runner.call(
        "coverage",
        accepted.assessment.candidate_id,
        "Advise on coverage gaps, excess, and repetition in the accepted cases. Use rejected cases "
        "as context only. If supplied, the calibration distribution is a coarse baseline, "
        "without a per-unit target. Return feedback only.",
        CoverageReport,
        **extra,
    )
