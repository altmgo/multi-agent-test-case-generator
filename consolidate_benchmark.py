#!/usr/bin/env python3
"""Consolidate generated units from multiple TCG runs into a single evaluable run."""

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

OUTPUT_DIR = Path("output")
RUN_TIMEZONE = ZoneInfo("America/Recife")
SOLUTIONS = ("zero-shot", "Multiagent")

def get_run_configs() -> list[tuple[Path, dict]]:
    runs = []
    for path in sorted(OUTPUT_DIR.glob("2026-*")):
        cfg_file = path / "configs.md"
        if not cfg_file.is_file():
            continue
        try:
            content = cfg_file.read_text(encoding="utf-8")
            m = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
            if m:
                cfg = json.loads(m.group(1))
                runs.append((path, cfg))
        except Exception:
            continue
    return runs

def consolidate(destination: Path | None = None) -> Path:
    runs = get_run_configs()
    if not runs:
        raise ValueError("Nenhum run encontrado em output/")

    if destination is None:
        now_str = datetime.now(RUN_TIMEZONE).strftime("%Y-%m-%d_%H-%M-%S")
        destination = OUTPUT_DIR / f"{now_str}_consolidated"

    destination.mkdir(parents=True, exist_ok=True)
    print(f"Consolidando resultados em: {destination}")

    consolidated_outcomes = {sol: {} for sol in SOLUTIONS}
    consolidated_units = set()
    history_log = []

    for run_path, cfg in runs:
        if run_path == destination:
            continue
        run_name = run_path.name
        outcomes = cfg.get("outcomes", {})
        for sol in SOLUTIONS:
            sol_dir = run_path / sol
            if not sol_dir.is_dir():
                continue
            for unit_id, outcome in outcomes.get(sol, {}).items():
                status = outcome.get("status")
                unit_dir = sol_dir / unit_id
                if status == "generated" and unit_dir.is_dir():
                    # Check if unit has markdown test case files
                    has_cases = any(unit_dir.glob("*/test cases/*.md"))
                    if has_cases or outcome.get("case_count", 0) > 0:
                        dest_sol_dir = destination / sol
                        dest_sol_dir.mkdir(exist_ok=True)
                        dest_unit_dir = dest_sol_dir / unit_id
                        if dest_unit_dir.exists():
                            shutil.rmtree(dest_unit_dir)
                        shutil.copytree(unit_dir, dest_unit_dir)
                        consolidated_outcomes[sol][unit_id] = outcome
                        consolidated_units.add(unit_id)
                        history_log.append(f"- [{run_name}] {sol}/{unit_id}: status={status}, cases={outcome.get('case_count')}")
                elif status == "failed":
                    history_log.append(f"- [{run_name}] {sol}/{unit_id}: FALHA em {outcome.get('error_stage')} ({outcome.get('error_type')}) [recuperado posteriormente]")

    # Build requirements_to_tests.md for each solution
    for sol in SOLUTIONS:
        sol_dir = destination / sol
        sol_dir.mkdir(exist_ok=True)
        lines = [f"# {sol} · Requirements to tests"]
        for unit_id in sorted(consolidated_outcomes[sol].keys()):
            outcome = consolidated_outcomes[sol][unit_id]
            lines.extend(["", f"## {unit_id}", "", f"Status · {outcome.get('status')}"])
        (sol_dir / "requirements_to_tests.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    all_units = sorted(consolidated_units)
    config = {
        "model": "gemini-3.5-flash-lite",
        "solutions": list(SOLUTIONS),
        "units": all_units,
        "agents": ["analyst", "coverage", "critic", "validator"],
        "output_modes": {name: "batch" for name in SOLUTIONS},
        "max_rounds": 2,
        "generation_retries": 3,
        "max_retry_wait_seconds": 60,
        "groq_tokens_per_minute": None,
        "reasoning_effort": None,
        "timezone": "America/Recife",
        "credential": ".env:GOOGLE_API_KEY",
        "status": "completed" if all(len(consolidated_outcomes[s]) == len(all_units) for s in SOLUTIONS) else "partial",
        "outcomes": consolidated_outcomes,
    }

    markdown_content = (
        "# Experiment configuration\n\n"
        "## Rastreabilidade de lotes e histórico de execução\n\n"
        + "\n".join(history_log) + "\n\n"
        "```json\n"
        f"{json.dumps(config, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )

    (destination / "configs.md").write_text(markdown_content, encoding="utf-8")
    print(f"✅ Consolidação finalizada com sucesso em: {destination}")
    for sol in SOLUTIONS:
        print(f"  - {sol}: {len(consolidated_outcomes[sol])}/{len(all_units)} unidades")

    return destination

if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    consolidate(dest)
