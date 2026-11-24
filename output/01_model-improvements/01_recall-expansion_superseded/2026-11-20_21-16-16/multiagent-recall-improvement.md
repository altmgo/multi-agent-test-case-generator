# Multiagent: aumento de recall e geração por tipos de cenários

## Configuration
- Solution: `Multiagent`
- Enabled agents: `analyst`, `critic`, `validator`, `coverage`
- Model: `gemini-3.5-flash-lite`
- Output mode: `per_requirement`
- Units: `e2edev_bench_01`, `e2edev_bench_02`, `e2edev_bench_03`, `e2edev_bench_04`, `firefox_bookmarks`, `firefox_browser_history`, `firefox_password_manager`, `firefox_themes`

## Goal
Aumentar o recall do Multiagent que estava estagnado em ~0.64. A meta principal era superar o gargalo do limite rígido de no máximo 2 casos por requisito ("at most two focused cases"), incentivando a geração de múltiplos tipos de cenários (Normal, Edge, Boundary, Error/Abnormal) suportados pelos requisitos, além de passar a utilizar o modo `per_requirement` e substituir o baseline `zero-shot` por `zero-shot`.

## Alterações feitas no commit
As alterações que originaram este run focaram na expansão de cobertura e enriquecimento de cenários:
1. **Generator (`src/multiagent/generator.py`)**: Substituição do limite de 2 casos por instrução para gerar um caso por tipo distinto de cenário (*Normal, Edge, Boundary, Error/Abnormal*) quando suportado pelo texto do requisito, evitando colapsar cenários distintos.
2. **Analyst (`src/multiagent/analyst.py`)**: Enumeração dos tipos de cenários esperados por requisito (*Normal, Edge, Boundary, Abnormal/Error*) para orientar o gerador.
3. **Critic (`src/multiagent/selection.py`)**: Atualização do `REVIEW_RUBRIC` para sinalizar falta de variantes quando o requisito explicita múltiplos cenários e solicitar revisão.
4. **Coverage (`src/multiagent/coverage.py`)**: Auditoria de cobertura verificando presença de tipos de cenários explicitados e apontando lacunas como *gaps*.
5. **Baseline Zero-Shot (`src/zero_shot/`, `src/tcg/cli.py`, `src/evaluate/reader.py`)**: Renomeação e transição do baseline `zero-shot` para `zero-shot`.
6. **Modo de Saída**: Execução com `--output-mode per_requirement` nos benchmarks avaliados.

## Results
- Unit coverage: `1.0`
- Generated cases: `177`
- Reference cases: `104`
- Matched cases: `95`
- Precision: `0.536723163841808`
- Recall: `0.9134615384615384`
- F1: `0.6761565836298933`
- Revision rounds across traces: `0`

## Impact analysis
O recall atingiu a marca expressiva de **0.9135** (95 de 104 casos de referência cobertos), confirmando que a eliminação do teto artificial de 2 casos por requisito e o modo `per_requirement` resolveram com sucesso o problema de subgeração em requisitos complexos (ex.: `e2edev_bench_01`, `02` e `03` mantiveram precisão de 1.0 com recall completo).

No entanto, houve um efeito colateral severo na precisão global, que caiu para **0.5367** devido à supergeração em requisitos atômicos e simples (especialmente no dataset *Firefox*, ex.: `firefox_themes` gerou 28 casos para 7 referências, precisão 0.25). O modelo passou a especular e fabricar cenários de borda/erro (ex.: arquivos corrompidos, falhas de rede não documentadas) mesmo onde o requisito continha apenas uma asserção declarativa de interface. Além disso, as rodadas de revisão permaneceram em 0, pois o Critic não barrou a supergeração como blocker. Isso motivou o refinamento subsequente para conter cenários especulativos.
