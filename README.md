# Multi-Agent Test Case Generator

Gera casos de teste de alto nível a partir de requisitos de software
normalizados e compara as saídas com casos de referência. O projeto foi criado
para estudar como diferentes estratégias de geração — incluindo uma esteira
multiagente — afetam precisão, recall e F1 na geração de testes.

> O gerador produz documentação de casos de teste. Ele não executa testes na
> aplicação sob teste.

## Visão geral

O fluxo de trabalho tem duas etapas independentes:

```text
Requisitos normalizados ──> tcg run ──> Casos de teste em Markdown
                                              │
Casos de referência ──────────────────────────┘
                                              │
                                      evaluate ──> Métricas e pareamentos
```

O comando `tcg run` gera casos de teste. O comando `evaluate` compara os
casos gerados com os casos de referência do conjunto de dados usando embeddings
Gemini e similaridade cosseno.

## Estratégias implementadas

| Estratégia | Nome na CLI | Como funciona |
| --- | --- | --- |
| Zero-shot | `zero-shot` | Uma chamada gera casos a partir do conjunto completo de requisitos da unidade. |
| Grounded High-Level | `GHL` | Seleciona técnicas de teste de uma lista fixa e gera casos por técnica. |
| Multiagent | `Multiagent` | Gera casos e pode acionar agentes de análise, crítica, validação, cobertura e revisão. |

### Esteira Multiagent

O Multiagent sempre possui um Generator. Os agentes abaixo são opcionais:

| Agente | Responsabilidade |
| --- | --- |
| `analyst` | Identifica comportamentos e cenários explicitamente descritos nos requisitos. |
| `critic` | Revisa cobertura, distinção entre cenários e necessidade de revisão. Também habilita o fallback determinístico de cenários explícitos. |
| `validator` | Verifica fundamentação, rastreabilidade e problemas bloqueadores nos casos propostos. |
| `coverage` | Produz um parecer consultivo de lacunas, excesso e repetição após a escolha do candidato aceito. |

Quando Critic ou Validator solicitam uma revisão, a orquestração pode gerar até
duas rodadas de candidatos e selecionar a melhor alternativa. Os traces dessa
decisão ficam em `intermediate/` dentro da unidade Multiagent.

## Requisitos

- Python 3.11 ou superior
- Uma chave de API compatível com o modelo escolhido
- Acesso de rede ao provedor durante geração e, para avaliação, ao Gemini

Modelos disponíveis atualmente:

| Modelo | Variável no `.env` | Provedor |
| --- | --- | --- |
| `gemini-3.5-flash-lite` | `GOOGLE_API_KEY` | Gemini |
| `gemini-3.8-flash` | `GOOGLE_API_KEY` | Gemini |
| `openai/gpt-oss-120b` | `GROQ_API_KEY` | Groq |

## Instalação

Execute os comandos na raiz do repositório:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Crie um arquivo `.env` na raiz. Para Gemini:

```dotenv
GOOGLE_API_KEY=sua_chave_aqui
```

Para Groq:

```dotenv
GROQ_API_KEY=sua_chave_aqui
```

O `.env` não deve ser versionado. Se a virtualenv foi ativada antes de mover o
projeto, abra um novo terminal e ative a `.venv` criada na raiz atual.

## Início rápido

O exemplo abaixo executa as três estratégias em duas unidades. O Zero-shot usa
modo `batch`; GHL e Multiagent usam `per_requirement`.

```bash
tcg run \
  --model gemini-3.5-flash-lite \
  --solutions zero-shot GHL Multiagent \
  --units e2edev_bench_01.json firefox_bookmarks.json \
  --agents analyst critic validator coverage \
  --output-mode per_requirement \
  --output-dir output/quickstart
```

Ao final, a CLI imprime uma pasta com timestamp, por exemplo:

```text
Output: output/quickstart/2026-11-23_14-30-00
```

Avalie essa execução com:

```bash
evaluate \
  --results-dir output/quickstart/2026-11-23_14-30-00 \
  --embedding-model gemini-embedding-2
```

## Gerando casos de teste

### Comando básico

```bash
tcg run \
  --model MODEL \
  --solutions SOLUTION [SOLUTION ...] \
  [--units FILE.json [FILE.json ...]] \
  [--datasets e2edev firefox] \
  [--agents analyst critic validator coverage] \
  [--output-mode batch|per_requirement|per_case] \
  [--data-dir data/normalized] \
  [--output-dir output]
```

Execute `tcg run --help` para a lista completa de argumentos.

### Selecionando unidades

`--units` recebe nomes de arquivos de `data/normalized/`, incluindo a extensão
`.json`:

```bash
tcg run \
  --model gemini-3.5-flash-lite \
  --solutions Multiagent \
  --units e2edev_bench_03.json firefox_password_manager.json \
  --agents analyst critic validator coverage \
  --output-mode per_requirement
```

Sem `--units`, a CLI processa todas as unidades elegíveis. Os manifestos em
`data/normalized/manifests/` não são tratados como unidades de geração.

Também é possível filtrar por conjunto:

```bash
tcg run \
  --model gemini-3.5-flash-lite \
  --solutions Multiagent \
  --datasets firefox \
  --agents analyst critic validator coverage \
  --output-mode batch
```

### Modos de saída

| Modo | GHL e Multiagent | Quando usar |
| --- | --- | --- |
| `batch` | Uma chamada para o conjunto de requisitos da unidade | Menor número de chamadas e execução mais rápida. |
| `per_requirement` | Uma chamada por requisito | Maior granularidade e rastreabilidade; indicado para os experimentos comparativos do projeto. |
| `per_case` | Uma chamada por caso solicitado | Maior granularidade operacional. |

O Zero-shot sempre usa `batch`, mesmo quando outro modo é informado na linha de
comando.

### Configurações Multiagent

Para ativar todos os agentes opcionais:

```bash
--agents analyst critic validator coverage
```

Para executar apenas o Generator, passe `--agents` sem nomes:

```bash
tcg run \
  --model gemini-3.5-flash-lite \
  --solutions Multiagent \
  --units e2edev_bench_01.json \
  --agents \
  --output-mode batch
```

Para uma ablação, omita somente o agente investigado. Por exemplo, sem
Coverage:

```bash
tcg run \
  --model gemini-3.5-flash-lite \
  --solutions Multiagent \
  --units e2edev_bench_01.json \
  --agents analyst critic validator \
  --output-mode per_requirement \
  --output-dir output/02_ablation/no-coverage
```

## Avaliando resultados

```bash
evaluate \
  --results-dir CAMINHO_DA_EXECUCAO \
  --embedding-model gemini-embedding-2 \
  [--data-dir data/normalized]
```

O avaliador usa `GOOGLE_API_KEY`, inclusive quando os casos foram gerados com
Groq. Modelos de embeddings disponíveis:

- `gemini-embedding-2`
- `gemini-embedding-001`

Para cada unidade, a avaliação faz pareamento um a um entre casos gerados e de
referência por similaridade cosseno, usando limiar de 0,70. Os relatórios
agregados apresentam:

- **Precisão**: fração dos casos gerados que encontrou correspondência.
- **Recall**: fração dos casos de referência que foi encontrada.
- **F1**: média harmônica entre precisão e recall.
- **Cobertura de unidades**: proporção de unidades avaliáveis concluídas.

Uma nova avaliação reutiliza resultados já compatíveis com o mesmo modelo de
embeddings. Ela substitui relatórios automáticos, mas não substitui arquivos
com revisão humana.

## Estrutura de entrada e saída

### Dados de entrada

```text
data/
├── normalized/              # Unidades usadas pela CLI
│   ├── e2edev_bench_*.json
│   ├── firefox_*.json
│   └── manifests/            # Metadados, não unidades de geração
└── raw/                     # Fontes originais, quando disponíveis
```

Cada JSON normalizado contém requisitos, casos de referência e metadados da
unidade. Durante a geração, somente os requisitos são enviados ao modelo; os
casos de referência são excluídos do prompt e usados somente no `evaluate`.

### Artefatos de uma execução

```text
output/<grupo>/<timestamp>/
├── configs.md               # Modelo, soluções, unidades, agentes e status
├── <solução>/
│   ├── requirements_to_tests.md
│   └── <unidade>/
│       ├── <requirement-id>/
│       │   ├── requirement.md
│       │   └── test cases/*.md
│       ├── intermediate/    # Apenas Multiagent: tentativas e decisões
│       ├── results.json     # Criado por evaluate
│       ├── results.csv      # Criado por evaluate
│       └── semantic_matches.json
└── comparison.json          # Criado por evaluate
```

Uma execução parcial preserva todos os artefatos concluídos e registra falhas
em `configs.md`. Não compare métricas de uma execução parcial com uma execução
completa. Quando uma experiência for produzida em várias execuções parciais,
consolide somente as unidades completas em uma nova pasta antes de avaliar.

## Limites, quotas e falhas transitórias

Uma chamada tem uma tentativa inicial e até três retentativas. Para erros
gerais, as esperas são 2, 4 e 8 segundos; para limite de taxa, são 15, 30 e
60 segundos. Uma resposta de quota esgotada ou um `Retry-After` acima de 60
segundos encerra a execução como parcial e preserva as saídas concluídas.

O Groq aplica ainda uma janela local de 60 segundos com orçamento de 8.000
tokens e intervalo mínimo de dois segundos entre requisições. O Gemini e o
Groq podem devolver erros temporários de indisponibilidade; reexecutar apenas
as unidades falhas em um novo diretório é a forma segura de recuperar o
experimento.

## Experimentos e resultados existentes

Os resultados do repositório são organizados em três grupos:

| Diretório | Conteúdo |
| --- | --- |
| `output/00_baseline-metrics_reference/` | Referência inicial de métricas. |
| `output/01_model-improvements/` | Cronologia de hipóteses, melhorias retidas e experiências revertidas. Leia `CHRONOLOGY.md`. |
| `output/02_ablation/` | Remoção de agentes individuais e análise comparativa em `AGENT_ABLATION_ANALYSIS.md`. |

## Implementação

```text
src/
├── tcg/          # CLI, modelos de dados, runtime de provedores e persistência
├── multiagent/   # Orquestração, agentes, seleção e estado de revisão
├── ghl/          # Seleção de técnicas e geração grounded high-level
├── zero_shot/    # Geração em uma única chamada
└── evaluate/     # Embeddings, pareamento, métricas e relatórios
```

O catálogo de técnicas GHL está em `src/ghl/__init__.py` e foi inspirado no
fluxo descrito por [Masuda et al.](https://arxiv.org/html/2510.03641v1#S3).

## Desenvolvimento

Depois de alterar o código, valide a importação dos comandos instalados:

```bash
python -c "import tcg.runtime, evaluate.cli; print('imports OK')"
tcg run --help
evaluate --help
```

Para contribuir, preserve a separação entre geração e avaliação: o gerador não
deve receber os casos de referência, e o avaliador deve ler somente os casos
finais publicados na pasta de saída.

## Limitações conhecidas

- A avaliação semântica é uma aproximação baseada em embeddings; ela não
  substitui revisão humana de qualidade de testes.
- Os resultados de geração são estocásticos; comparações fortes exigem mais de
  uma execução por configuração.
- Quotas e indisponibilidade do provedor podem interromper uma execução.
- A esteira não executa os casos gerados nem verifica a aplicação real.
