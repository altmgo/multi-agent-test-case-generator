"""Command line entry point for test case generation."""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values

from ghl import GHLFailure, generate_ghl
from multiagent import MultiagentFailure, run_multiagent
from one_shot import generate_one_shot

from .data import DATASETS, select_units
from .output import RUN_TIMEZONE, reserve_run, save_unit, write_text
from .runtime import (
    GENERATION_MODELS, GROQ_TOKENS_PER_MINUTE, MAX_RETRY_WAIT_SECONDS,
    ModelRuntime, credential_variable, sum_usage,
)
from .schemas import GenerationResult, Unit, generation_input

SOLUTIONS = ("one-shot", "GHL", "Multiagent")
OPTIONAL_AGENTS = ("analyst", "critic", "validator", "coverage")
OUTPUT_MODES = ("batch", "per_requirement", "per_case")
MAX_ROUNDS = 2


def _solution_name(value: str) -> str:
    for solution in SOLUTIONS:
        if solution.casefold() == value.casefold():
            return solution
    raise argparse.ArgumentTypeError(f"Choose one of {', '.join(SOLUTIONS)}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tcg", description="Generate high-level test cases.")
    run = parser.add_subparsers(dest="command", required=True).add_parser("run")
    run.add_argument("--model", choices=sorted(GENERATION_MODELS), required=True)
    run.add_argument("--solutions", type=_solution_name, choices=SOLUTIONS, nargs="+", action="extend", required=True)
    run.add_argument("--units", nargs="+", action="extend", default=[], metavar="FILE.json",
                     help="Normalized filenames. Defaults to all eligible files when no filter is given.")
    run.add_argument("--datasets", choices=DATASETS, nargs="+", action="extend", default=[])
    run.add_argument("--agents", choices=OPTIONAL_AGENTS, nargs="*", action="extend",
                     help="Optional Multiagent stages. Pass without names to disable them.")
    run.add_argument("--output-mode", choices=OUTPUT_MODES, default="batch",
                     help="Output scope for GHL and Multiagent. One-shot uses batch.")
    run.add_argument("--data-dir", type=Path, default=Path("data/normalized"))
    run.add_argument("--output-dir", "--results-dir", type=Path, default=Path("output"))
    return parser


def _agents(options: argparse.Namespace) -> set[str]:
    if "Multiagent" not in options.solutions and options.agents is not None:
        raise ValueError("--agents requires Multiagent")
    if options.agents is not None:
        return set(options.agents)
    if "Multiagent" not in options.solutions or not sys.stdin.isatty():
        return set()
    try:
        selected = set(input(f"Optional agents ({', '.join(OPTIONAL_AGENTS)}): ").split())
    except EOFError:
        return set()
    if unknown := selected.difference(OPTIONAL_AGENTS):
        raise ValueError("Unknown optional agents: " + ", ".join(sorted(unknown)))
    return selected


async def _run(
    run: Path,
    options: argparse.Namespace,
    units: list[Unit],
    agents: set[str],
    runtime: ModelRuntime,
) -> int:
    outcomes = {}
    config = {
        "model": options.model,
        "solutions": options.solutions,
        "units": [unit.id for unit in units],
        "agents": sorted(agents),
        "output_modes": {name: "batch" if name == "one-shot" else options.output_mode for name in options.solutions},
        "max_rounds": MAX_ROUNDS,
        "generation_retries": runtime.retries,
        "max_retry_wait_seconds": MAX_RETRY_WAIT_SECONDS,
        "groq_tokens_per_minute": GROQ_TOKENS_PER_MINUTE if runtime.is_groq else None,
        "reasoning_effort": "low" if runtime.is_groq else None,
        "timezone": str(RUN_TIMEZONE),
        "credential": f".env:{credential_variable(options.model)}",
        "status": "interrupted",
        "outcomes": outcomes,
    }
    failed = 0
    try:
        for solution in options.solutions:
            directory = run / solution
            directory.mkdir()
            lines = [f"# {solution} · Requirements to tests"]
            outcomes[solution] = {}
            for unit in units:
                source = generation_input(unit)
                usage_start = len(runtime.usage_records)
                failure = None
                failure_stage = None
                interrupted = None
                try:
                    if solution == "one-shot":
                        result = await generate_one_shot(source, runtime)
                    elif solution == "GHL":
                        result = await generate_ghl(source, runtime, output_mode=options.output_mode)
                    else:
                        result = await run_multiagent(
                            source, runtime, agents, MAX_ROUNDS, output_mode=options.output_mode,
                        )
                except GHLFailure as error:
                    result, failure = error.partial_result, error.error_type
                    failure_stage = error.stage
                except MultiagentFailure as error:
                    result, failure = error.partial_result, error.failure.error_type
                    failure_stage = error.failure.stage
                except asyncio.CancelledError as error:
                    interrupted = error
                    failure = type(error).__name__
                    partial = getattr(error, "tcg_partial", None)
                    result = partial[1] if partial else GenerationResult(
                        cases=[], usage=sum_usage(runtime.usage_records[usage_start:]),
                    )
                except Exception as error:
                    failure = type(error).__name__
                    result = GenerationResult(cases=[], usage=sum_usage(runtime.usage_records[usage_start:]))
                status = "interrupted" if interrupted is not None else "failed" if failure else "generated"
                lines.extend(save_unit(directory, unit, result, status))
                write_text(directory / "requirements_to_tests.md", "\n".join(lines) + "\n")
                outcomes[solution][unit.id] = {
                    "status": status,
                    "case_count": len(result.cases),
                    "usage": result.usage.model_dump(mode="json"),
                    "selected_techniques": result.selected_techniques,
                    "technique_rationales": result.technique_rationales,
                    "error_type": failure,
                    "error_stage": failure_stage,
                }
                if interrupted is not None:
                    raise interrupted
                if failure:
                    failed += 1
                    location = f" at {failure_stage}" if failure_stage else ""
                    print(f"{solution}/{unit.id}: generation failed{location} ({failure})", file=sys.stderr)
                if runtime.stop_reason is not None:
                    config["status"] = "partial"
                    config["stop_reason"] = runtime.stop_reason
                    return 1
        config["status"] = "partial" if failed else "completed"
        return int(bool(failed))
    except (OSError, ValueError):
        config["status"] = "failed"
        raise
    finally:
        try:
            write_text(run / "configs.md", "# Experiment configuration\n\n```json\n"
                       + json.dumps(config, ensure_ascii=False, indent=2) + "\n```\n")
        finally:
            await runtime.aclose()


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    options = parser.parse_args(argv)
    options.solutions = list(dict.fromkeys(options.solutions))
    try:
        agents = _agents(options)
        units = select_units(options.data_dir, options.units, options.datasets)
        dotenv_path = Path(".env")
        variable = credential_variable(options.model)
        api_key = (dotenv_values(dotenv_path, interpolate=False).get(variable) or "").strip()
        if not api_key:
            raise ValueError(f"Set {variable} in .env")
        runtime = ModelRuntime(options.model, api_key=api_key)
        run = reserve_run(options.output_dir, lambda: datetime.now(timezone.utc))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Output: {run}")
    try:
        return asyncio.run(_run(run, options, units, agents, runtime))
    except (KeyboardInterrupt, asyncio.CancelledError):
        return 130
    except (OSError, ValueError) as error:
        print(f"tcg: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
