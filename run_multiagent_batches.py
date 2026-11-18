#!/usr/bin/env python3
"""Run Multiagent generation in balanced batches to respect Gemini rate limits."""

import subprocess
import sys
import time
from pathlib import Path

PYTHON_EXE = sys.executable

BATCHES = [
    {
        "name": "Lote 1/6 (Firefox - 15 unidades)",
        "args": [
            "--datasets", "firefox"
        ],
    },
    {
        "name": "Lote 2/6 (E2EDev Parte 1 - 10 unidades)",
        "args": [
            "--units",
            "e2edev_bench_01.json", "e2edev_bench_02.json", "e2edev_bench_03.json", "e2edev_bench_04.json",
            "e2edev_bench_05.json", "e2edev_bench_06.json", "e2edev_bench_07.json", "e2edev_bench_08.json",
            "e2edev_bench_09.json", "e2edev_bench_10.json",
        ],
    },
    {
        "name": "Lote 3/6 (E2EDev Parte 2 - 10 unidades)",
        "args": [
            "--units",
            "e2edev_bench_11.json", "e2edev_bench_12.json", "e2edev_bench_13.json", "e2edev_bench_15.json",
            "e2edev_bench_18.json", "e2edev_bench_19.json", "e2edev_bench_20.json", "e2edev_bench_21.json",
            "e2edev_bench_22.json", "e2edev_bench_24.json",
        ],
    },
    {
        "name": "Lote 4/6 (E2EDev Parte 3 - 10 unidades)",
        "args": [
            "--units",
            "e2edev_bench_25.json", "e2edev_bench_26.json", "e2edev_bench_27.json", "e2edev_bench_28.json",
            "e2edev_bench_29.json", "e2edev_bench_30.json", "e2edev_bench_32.json", "e2edev_bench_36.json",
            "e2edev_bench_37.json", "e2edev_bench_40.json",
        ],
    },
    {
        "name": "Lote 5/6 (E2EDev Parte 4 - 10 unidades)",
        "args": [
            "--units",
            "e2edev_bench_42.json", "e2edev_bench_44.json", "e2edev_bench_46.json", "e2edev_bench_48.json",
            "e2edev_bench_49.json", "e2edev_bench_51.json", "e2edev_bench_52.json", "e2edev_bench_57.json",
            "e2edev_bench_59.json", "e2edev_bench_60.json",
        ],
    },
    {
        "name": "Lote 6/6 (E2EDev Parte 5 - 6 unidades)",
        "args": [
            "--units",
            "e2edev_bench_601.json", "e2edev_bench_602.json", "e2edev_bench_603.json", "e2edev_bench_63.json",
            "e2edev_bench_64.json", "e2edev_bench_66.json",
        ],
    },
]

COMMON_FLAGS = [
    "-m", "tcg", "run",
    "--model", "gemini-3.5-flash-lite",
    "--solutions", "Multiagent",
    "--agents", "analyst", "critic", "validator", "coverage",
    "--output-mode", "batch",
]

def main() -> int:
    total_batches = len(BATCHES)
    start_batch = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    print(f"=== Iniciando execução do Multiagent em {total_batches} lotes ===")
    print("Modelo: gemini-3.5-flash-lite | Modo: batch | Agentes: analyst, critic, validator, coverage\n")

    for index, batch in enumerate(BATCHES[start_batch - 1:], start=start_batch):
        print(f"\n[{index}/{total_batches}] Executando: {batch['name']}...")
        cmd = [PYTHON_EXE] + COMMON_FLAGS + batch["args"]

        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"\n❌ Falha no lote {index} ({batch['name']}). Código: {result.returncode}")
            print(f"Para retomar deste lote adiante, rode: python {sys.argv[0]} {index}")
            return result.returncode

        print(f"✅ {batch['name']} concluído com sucesso!")
        if index < total_batches:
            pause = 20
            print(f"Aguardando {pause}s para estabilização de cota antes do próximo lote...")
            time.sleep(pause)

    print("\n🎉 Todos os 6 lotes do Multiagent foram concluídos com sucesso!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
