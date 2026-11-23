# Multiagent: recuperação de precisão e controle de cenários especulativos

## Configuration
- Solution: `Multiagent`
- Enabled agents: `analyst`, `critic`, `validator`, `coverage`
- Model: `gemini-3.5-flash-lite`
- Output mode: `per_requirement`
- Units: `e2edev_bench_01`, `e2edev_bench_02`, `e2edev_bench_03`, `e2edev_bench_04`, `firefox_bookmarks`, `firefox_browser_history`, `firefox_password_manager`, `firefox_themes`

## Goal
Recuperar a precisão do Multiagent (que havia caído para 0.5367 no run anterior) eliminando a supergeração e a fabricação de cenários especulativos/não suportados nos requisitos simples (como no Firefox), mantendo o recall elevado obtido com o modo `per_requirement`.

## Alterações feitas no commit (`9a95389`)
Neste commit (`zero shot e improvements`), foram refinados os prompts e rubricas para calibrar a granularidade da geração:
1. **Generator (`src/multiagent/generator.py`)**: Instrução explícita para fundamentar testes estritamente no texto do requisito, **proibindo terminantemente a invenção de condições especulativas ou hipotéticas** (ex.: corrupção de assets, erros de rede, redimensionamento de janela) não descritas. Para requisitos simples e atômicos (como presença de item de menu), foi delimitada a geração de exatamente um caso normal focado.
2. **Analyst (`src/multiagent/analyst.py`)**: Adicionada verificação de atomicidade do requisito: instruído a especificar apenas um caso Normal quando for requisito declarativo simples e a listar Edge/Boundary/Error apenas se o texto explicitar parâmetros, intervalos ou caminhos alternativos reais.
3. **Critic (`src/multiagent/selection.py`)**: Inclusão na rubrica para sinalizar casos especulativos e redundantes como solicitação de revisão.
4. **Coverage (`src/multiagent/coverage.py`)**: Instrução para auditar e apontar ativamente excesso (*excess / overgeneration*) de casos não fundamentados no texto.
5. **Consolidação do baseline Zero-Shot**: Ajustes finais em `src/zero_shot/`, `src/tcg/cli.py`, `src/tcg/runtime.py` e `src/evaluate/reader.py`.

## Results
- Unit coverage: `1.0`
- Generated cases: `86`
- Reference cases: `104`
- Matched cases: `82`
- Precision: `0.9534883720930233`
- Recall: `0.7884615384615384`
- F1: `0.8631578947368421`
- Revision rounds across traces: `0`

## Impact analysis
As alterações atingiram com sucesso a meta de recuperação da precisão sem sacrificar desproporcionalmente o recall:
- **Precisão**: Saltou de **0.5367** para **0.9535** (+0.4168), eliminando o ruído e os casos inválidos que haviam sido inflados no Firefox (total de casos gerados reduziu de 177 para 86).
- **Recall**: Manteve-se em um patamar muito alto de **0.7885** (82 de 104 referências), significativamente superior ao baseline inicial (~0.64).
- **F1-Score**: Alcançou **0.8632**, o maior score global consolidado do pipeline até então (superando os 0.781 do baseline consolidado e os 0.676 do run anterior).

A calibração do Analyst e Generator para respeitar a atomicidade dos requisitos provou ser o ajuste ideal entre abrangência e precisão, impedindo alucinações de cenários de teste em requisitos declarativos.
