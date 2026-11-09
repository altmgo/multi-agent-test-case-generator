"""Command-line entry point for local GHL-MAS experiments."""

import argparse
import asyncio
import hashlib
import json
import os
import platform
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from datasets import e2edev, firefox, profile
from evaluation.embeddings import EMBEDDING_INSTRUCTION, EMBEDDING_MODEL, Embedder, EmbeddingError, GeminiEmbedder
from evaluation.matching import SIMILARITY_THRESHOLD
from evaluation.metrics import aggregate, evaluate
from model_runtime import DEFAULT_CONTEXT_LIMIT, DEFAULT_OUTPUT_TOKENS, GENERATION_MODELS, ModelRuntime, Runtime, sum_usage
from persistence import RUN_TIMEZONE, SOLUTIONS, TIMESTAMP_FORMAT, reserve_run, save_unit, write_json, write_text
from schemas import EvaluationResult, GenerationResult, Unit, UsageRecord, generation_input
from solutions import ghl, one_shot
from solutions.multiagent import MultiagentFailure, run_multiagent
from solutions.multiagent.coverage import E2EDevCalibrationProfile
from solutions.multiagent.state import CANDIDATES_PER_ROUND, PROMPT_VERSION as MULTIAGENT_PROMPT_VERSION

RAW_DATA_DIR = Path("data/raw")
NORMALIZED_DATA_DIR = Path("data/normalized")
COVERAGE_PROFILE_PATH = Path("data/profiles/e2edev_coverage.json")
RESULTS_DIR = Path("results")
DEFAULT_OUTPUT_MODE = "batch"
OUTPUT_MODES = ("batch", "per_requirement", "per_case")
OPTIONAL_AGENTS = ("analyst", "critic", "validator", "coverage")
MAX_ROUNDS = 2
GENERATION_RETRIES = 0
CREDENTIAL_ENV_VARS = ("GOOGLE_API_KEY", "GEMINI_API_KEY")
EMBEDDING_MODEL_VERSION = EMBEDDING_MODEL

_ADAPTERS = {"firefox": firefox, "e2edev": e2edev}
_MANIFESTS = {"firefox": firefox.MANIFEST_PATH, "e2edev": Path("manifests/e2edev.json")}
_UNIT_ID = re.compile(r"(firefox|e2edev)_[A-Za-z0-9_-]{1,100}")
_PROMPTS = {
    "one-shot": one_shot.PROMPT_VERSION,
    "GHL": ghl.PROMPT_VERSION,
    "Multiagent": MULTIAGENT_PROMPT_VERSION,
}


@dataclass(frozen=True)
class SelectedUnit:
    unit: Unit
    dataset: str
    sha256: str

    def provenance(self) -> dict[str, str]:
        return {"dataset": self.dataset, "file": f"{self.unit.id}.json", "sha256": self.sha256}


def now() -> datetime:
    return datetime.now(timezone.utc)


def make_runtime(model: str) -> Runtime:
    return ModelRuntime(
        model, context_limit=DEFAULT_CONTEXT_LIMIT, output_tokens=DEFAULT_OUTPUT_TOKENS,
        retries=GENERATION_RETRIES,
    )


def make_embedder() -> Embedder:
    return GeminiEmbedder(model_version=EMBEDDING_MODEL_VERSION)


def _solution_name(value: str) -> str:
    for solution in SOLUTIONS:
        if solution.casefold() == value.casefold():
            return solution
    raise argparse.ArgumentTypeError(f"Choose one of {', '.join(SOLUTIONS)}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ghl-mas", description="Prepare and run GHL-MAS experiments.")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Normalize verified local dataset files.")
    datasets = prepare.add_subparsers(dest="dataset", required=True)
    firefox_parser = datasets.add_parser("firefox")
    firefox_parser.add_argument("--requirements", type=Path, default=RAW_DATA_DIR / "firefox/R-set.csv")
    firefox_parser.add_argument("--tests", type=Path, default=RAW_DATA_DIR / "firefox/T-set.csv")
    firefox_parser.add_argument("--output", type=Path, default=NORMALIZED_DATA_DIR)
    e2edev_parser = datasets.add_parser("e2edev")
    e2edev_parser.add_argument("--source", type=Path, default=RAW_DATA_DIR / "e2edev" / e2edev.SOURCE_COMMIT)
    e2edev_parser.add_argument("--commit", default=e2edev.SOURCE_COMMIT, help="Verified E2EDev source commit.")
    e2edev_parser.add_argument("--output", type=Path, default=NORMALIZED_DATA_DIR)
    e2edev_parser.add_argument("--profile", type=Path, help="Descriptive coverage profile JSON destination.")

    run = commands.add_parser("run", help="Run selected solutions on normalized units.")
    run.add_argument("--model", choices=sorted(GENERATION_MODELS), required=True)
    run.add_argument("--solutions", type=_solution_name, choices=SOLUTIONS, nargs="+", action="extend", required=True)
    run.add_argument("--units", nargs="+", action="extend", default=[], metavar="UNIT")
    run.add_argument("--datasets", choices=tuple(_ADAPTERS), nargs="+", action="extend", default=[])
    run.add_argument("--agents", choices=OPTIONAL_AGENTS, nargs="*", action="extend",
                     help="Optional Multiagent stages. Pass without names to disable them.")
    run.add_argument("--output-mode", choices=OUTPUT_MODES, default=DEFAULT_OUTPUT_MODE,
                     help="Output scope for GHL and Multiagent. One-shot always uses batch.")
    run.add_argument("--calibration-units", nargs="+", action="extend", default=[], metavar="UNIT",
                     help="Disjoint E2EDev unit IDs for the Multiagent coverage aggregate.")
    run.add_argument("--data-dir", type=Path, default=NORMALIZED_DATA_DIR)
    run.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    return parser


def _prepare(options: argparse.Namespace) -> None:
    if options.dataset == "firefox":
        units = firefox.prepare_firefox(options.requirements, options.tests, options.output)
    else:
        units = e2edev.prepare_e2edev(options.source, options.commit, options.output)
        destination = options.profile
        if destination is None:
            destination = options.output.parent / "profiles" / COVERAGE_PROFILE_PATH.name
        profile.save_coverage_profile(units, destination, dataset_version=options.commit)
    print(f"Prepared {sum(unit.generatable for unit in units)} units in {options.output}")


def _agents(options: argparse.Namespace) -> set[str]:
    if "Multiagent" not in options.solutions:
        if options.agents is not None:
            raise ValueError("--agents requires Multiagent")
        return set()
    if options.agents is not None:
        return set(options.agents)
    if not sys.stdin.isatty():
        return set()
    try:
        selected = set(input(f"Optional Multiagent agents ({', '.join(OPTIONAL_AGENTS)}), space-separated: ").split())
    except EOFError:
        return set()
    if unknown := selected.difference(OPTIONAL_AGENTS):
        raise ValueError("Unknown optional agents: " + ", ".join(sorted(unknown)))
    return selected


def _read_unit(data_dir: Path, unit_id: str) -> SelectedUnit:
    if unit_id == firefox.ARCHIVE_ID:
        raise ValueError("firefox_legacy is an archive and cannot be selected")
    match = _UNIT_ID.fullmatch(unit_id)
    if match is None:
        raise ValueError(f"Unknown or unsafe normalized unit ID: {unit_id!r}")
    path = data_dir / f"{unit_id}.json"
    if path.is_symlink():
        raise ValueError(f"Normalized unit cannot be a symbolic link: {unit_id}")
    try:
        content = path.read_bytes()
    except FileNotFoundError:
        raise ValueError(f"Unknown normalized unit: {unit_id}") from None
    unit = Unit.model_validate_json(content)
    if unit.id != unit_id or not unit.generatable:
        raise ValueError(f"Normalized unit is ineligible or has a mismatched ID: {unit_id}")
    requirement_ids = {requirement.id for requirement in unit.requirements}
    if len(requirement_ids) != len(unit.requirements) or len({case.id for case in unit.reference_cases}) != len(unit.reference_cases):
        raise ValueError(f"Duplicate normalized IDs in {unit_id}")
    if any(not requirement_ids.issuperset(case.requirement_ids) for case in unit.reference_cases):
        raise ValueError(f"Unknown reference requirement IDs in {unit_id}")
    return SelectedUnit(unit, match[1], hashlib.sha256(content).hexdigest())


def _selections(options: argparse.Namespace, agents: set[str]) -> tuple[list[SelectedUnit], list[SelectedUnit], E2EDevCalibrationProfile | None]:
    selected_ids = list(options.units)
    for dataset in dict.fromkeys(options.datasets):
        discovered = sorted(
            path.stem for path in options.data_dir.glob(f"{dataset}_*.json")
            if path.stem != firefox.ARCHIVE_ID
        )
        if not discovered:
            raise ValueError(f"No normalized {dataset} units found in {options.data_dir}")
        selected_ids.extend(discovered)
    if not selected_ids:
        raise ValueError("Select at least one --units or --datasets value")
    selected = [_read_unit(options.data_dir, unit_id) for unit_id in dict.fromkeys(selected_ids)]

    if not options.calibration_units:
        return selected, [], None
    if "coverage" not in agents or not any(item.dataset == "e2edev" for item in selected):
        raise ValueError("--calibration-units requires Multiagent coverage and evaluated E2EDev units")
    calibration = [_read_unit(options.data_dir, unit_id) for unit_id in dict.fromkeys(options.calibration_units)]
    if any(item.dataset != "e2edev" for item in calibration):
        raise ValueError("Calibration requires only E2EDev units")
    corpus = {item.unit.id: item.unit for item in (*selected, *calibration)}
    distribution = profile.calibration_profile(
        list(corpus.values()), {item.unit.id for item in calibration}, {item.unit.id for item in selected},
    )
    return selected, calibration, E2EDevCalibrationProfile.model_validate(distribution)


def _version(distribution: str) -> str | None:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return None


def _datasets_metadata(data_dir: Path, names: set[str]) -> dict:
    records = {}
    for dataset in sorted(names):
        adapter = _ADAPTERS[dataset]
        source_hash = hashlib.sha256(Path(adapter.__file__).read_bytes()).hexdigest()
        relative = _MANIFESTS[dataset]
        path = data_dir / relative
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError("Dataset manifest cannot be a symbolic link")
        entry = {
            "adapter": adapter.__name__,
            "adapter_sha256": source_hash,
            "expected_source_commit": e2edev.SOURCE_COMMIT if dataset == "e2edev" else None,
            "source_version": None,
            "manifest": None,
        }
        if path.is_file():
            content = path.read_bytes()
            try:
                manifest = json.loads(content)
                version = manifest["source"].get("commit" if dataset == "e2edev" else "version")
                taxonomy = manifest.get("taxonomy", {}).get("version")
            except (AttributeError, KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid dataset manifest: {relative}") from error
            if dataset == "e2edev" and version != e2edev.SOURCE_COMMIT:
                raise ValueError(f"Unsupported source commit in dataset manifest: {relative}")
            entry["source_version"] = version
            entry["taxonomy_version"] = taxonomy
            entry["manifest"] = {"file": relative.as_posix(), "sha256": hashlib.sha256(content).hexdigest()}
        records[dataset] = entry
    return records


def _configuration(
    options: argparse.Namespace, agents: set[str], selected: list[SelectedUnit],
    calibration: list[SelectedUnit], distribution: E2EDevCalibrationProfile | None,
) -> dict:
    env = next((name for name in CREDENTIAL_ENV_VARS if os.getenv(name, "").strip()), None)
    datasets = _datasets_metadata(options.data_dir, {item.dataset for item in (*selected, *calibration)})
    return {
        "status": "running",
        "timezone": RUN_TIMEZONE.key,
        "timestamp_format": TIMESTAMP_FORMAT,
        "model": options.model,
        "available_models": sorted(GENERATION_MODELS),
        "embedding_model": EMBEDDING_MODEL,
        "embedding_model_version": EMBEDDING_MODEL_VERSION,
        "embedding_instruction": EMBEDDING_INSTRUCTION,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "candidates_per_round": CANDIDATES_PER_ROUND,
        "max_rounds": MAX_ROUNDS,
        "generation_retries": GENERATION_RETRIES,
        "context_limit": DEFAULT_CONTEXT_LIMIT,
        "output_tokens": DEFAULT_OUTPUT_TOKENS,
        "default_output_mode": DEFAULT_OUTPUT_MODE,
        "output_modes": {solution: "batch" if solution == "one-shot" else options.output_mode for solution in options.solutions},
        "paths": {
            "data": str(options.data_dir.resolve()),
            "results": str(options.results_dir.resolve()),
            "default_data": str(NORMALIZED_DATA_DIR),
            "default_results": str(RESULTS_DIR),
        },
        "solutions": options.solutions,
        "multiagent_agents": (
            ["orchestrator", "generator", *sorted(agents)] if "Multiagent" in options.solutions else []
        ),
        "versions": {
            "python": platform.python_version(),
            **{name: _version(name) for name in ("ghl-mas", "pydantic", "pydantic-ai-slim", "google-genai", "numpy", "scipy")},
            "prompts": {solution: _PROMPTS[solution] for solution in options.solutions},
        },
        "credential": {"present": env is not None, "reference": env, "environment_variables": list(CREDENTIAL_ENV_VARS)},
        "datasets": datasets,
        "units": {item.unit.id: item.provenance() for item in selected},
        "calibration": None if distribution is None else {
            "profile_version": profile.PROFILE_VERSION,
            "dataset_version": datasets["e2edev"]["source_version"],
            "unit_ids": [item.unit.id for item in calibration],
            "evaluated_unit_ids": [item.unit.id for item in selected],
            "units": {item.unit.id: item.provenance() for item in calibration},
            "aggregate": distribution.model_dump(mode="json"),
        },
    }


def _write_configs(run: Path, config: dict) -> None:
    data = json.dumps(config, ensure_ascii=False, allow_nan=False, indent=2)
    write_text(run / "configs.md", f"# Experiment configuration\n\n```json\n{data}\n```\n")


async def _generate(
    solution: str, item: SelectedUnit, runtime: Runtime, agents: set[str],
    output_mode: str, calibration: E2EDevCalibrationProfile | None,
) -> GenerationResult:
    source = generation_input(item.unit)
    if solution == "one-shot":
        return await one_shot.generate_one_shot(source, runtime)
    if solution == "GHL":
        return await ghl.generate_ghl(source, runtime, output_mode=output_mode)
    return await run_multiagent(
        source, runtime, agents, MAX_ROUNDS, output_mode=output_mode,
        calibration_profile=calibration if item.dataset == "e2edev" else None,
    )


async def _execute(
    run: Path, options: argparse.Namespace, selected: list[SelectedUnit], agents: set[str],
    calibration: E2EDevCalibrationProfile | None, config: dict,
) -> int:
    outcomes: dict[str, dict] = {solution: {} for solution in options.solutions}
    evaluations: dict[str, dict[str, EvaluationResult]] = {solution: {} for solution in options.solutions}
    runtime = embedder = None
    config["outcomes"] = outcomes
    config["status"] = "interrupted"
    try:
        for solution in options.solutions:
            for item in selected:
                unit = item.unit
                attempts_start = len(runtime.usage_records) if runtime is not None else 0
                calls_start = len(getattr(runtime, "call_records", ()))
                result = failure = evaluation = None
                embedding_usage = UsageRecord(input_tokens=0, output_tokens=0)
                embedding_requests = 0

                try:
                    if runtime is None:
                        runtime = make_runtime(options.model)
                    result = await _generate(solution, item, runtime, agents, options.output_mode, calibration)
                except MultiagentFailure as error:
                    result = error.partial_result
                    detail = result.trace["failure"]
                    failure = {"stage": detail["stage"], "error_type": detail["error_type"]}
                except Exception as error:
                    failure = {"stage": "generation", "error_type": type(error).__name__}

                attempts = runtime.usage_records[attempts_start:] if runtime is not None else []
                calls = getattr(runtime, "call_records", ())[calls_start:]
                if result is None:
                    if calls:
                        failure["stage"] = calls[-1].stage
                    result = GenerationResult(cases=[], usage=sum_usage(attempts), prompt_version=_PROMPTS[solution])

                if failure is None:
                    try:
                        if embedder is None:
                            embedder = make_embedder()
                        evaluation = evaluate(unit, result.cases, embedder)
                    except EmbeddingError as error:
                        failure = {"stage": "evaluation", "error_type": type(error).__name__}
                        embedding_usage, embedding_requests = error.usage, error.request_count
                    except Exception as error:
                        failure = {"stage": "evaluation", "error_type": type(error).__name__}
                        embedding_usage, embedding_requests = UsageRecord(), None

                try:
                    save_unit(
                        run, solution, unit, result, evaluation, failure=failure,
                        generation_attempts=attempts, generation_calls=calls,
                        embedding_usage=embedding_usage, embedding_requests=embedding_requests,
                    )
                except (ValueError, OSError) as error:
                    failure = {"stage": "persistence", "error_type": type(error).__name__}
                else:
                    if evaluation is not None:
                        evaluations[solution][unit.id] = evaluation

                if failure is None:
                    outcomes[solution][unit.id] = {"status": evaluation.status}
                else:
                    outcomes[solution][unit.id] = {"status": "failed", "failure": failure}
                    print(f"{solution}/{unit.id}: {failure['stage']} failed ({failure['error_type']})", file=sys.stderr)

        comparison = aggregate(evaluations, selected_unit_ids=(item.unit.id for item in selected))
        write_json(run / "comparison.json", comparison.model_dump(mode="json"))
        config["comparison"] = "comparison.json"
        completed = sum(len(units) for units in evaluations.values())
        total = len(selected) * len(options.solutions)
        config["status"] = "completed" if completed == total else "partial" if completed else "failed"
    finally:
        try:
            close = getattr(embedder, "close", None)
            if close is not None:
                close()
        finally:
            _write_configs(run, config)
    return 0 if config["status"] == "completed" else 1


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    options = parser.parse_args(argv)
    if options.command == "prepare":
        try:
            _prepare(options)
        except (OSError, ValueError) as error:
            parser.error(str(error))
        return 0

    options.solutions = list(dict.fromkeys(options.solutions))
    try:
        agents = _agents(options)
        selected, calibration, distribution = _selections(options, agents)
        config = _configuration(options, agents, selected, calibration, distribution)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    run = reserve_run(options.results_dir, now)
    config["reserved_at"] = datetime.strptime(run.name, TIMESTAMP_FORMAT).replace(tzinfo=RUN_TIMEZONE).isoformat()
    _write_configs(run, config)
    print(run)
    return asyncio.run(_execute(run, options, selected, agents, distribution, config))


if __name__ == "__main__":
    raise SystemExit(main())
