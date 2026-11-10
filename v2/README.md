# Ferramentas de pesquisa · v2

As ferramentas usam os JSONs de `data/normalized/` que acompanham o repositório.
Rode os comandos abaixo a partir de `v2/` com Python 3.11 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Crie `v2/.env` e defina `GOOGLE_API_KEY` com sua chave Gemini. O arquivo
fica fora do Git. A CLI lê a chave do `.env` no diretório atual.

## tcg · Test Case Generator

```bash
tcg run \
  --model gemini-3.5-flash-lite \
  --solutions one-shot GHL Multiagent \
  --units firefox_bookmarks.json e2edev_bench_01.json \
  --agents analyst critic validator coverage \
  --output-mode batch
```

Omita `--units` para gerar a partir de todos os JSONs elegíveis de
`data/normalized/`. Os manifestos ficam fora da geração. Use o nome completo com `.json` para
selecionar uma unidade. A CLI extrai os requisitos de cada arquivo e ignora
os casos de referência, inclusive na etapa de cobertura do Multiagent.

O GHL usa um catálogo fixo em `src/ghl/__init__.py`, inspirado no fluxo de
[Masuda et al.](https://arxiv.org/html/2510.03641v1#S3). O Gemini escolhe as
técnicas aplicáveis a partir dos requisitos e do catálogo, depois gera casos
para cada técnica escolhida. As escolhas e justificativas ficam em `configs.md`.

Use `--output-dir` para escolher outro destino e `--data-dir` para indicar
outros JSONs normalizados. A pasta de cada execução segue o formato
`output/AAAA-MM-DD_HH-MM-SS/` no fuso `America/Recife`. Cada solução tem
`requirements_to_tests.md` e uma pasta por unidade, com `requirement.md`
e `test cases/*.md` por requisito. A execução registra a configuração em
`configs.md` e o Multiagent grava suas revisões em `intermediate/`.
A CLI gera casos com Gemini. Não executa os casos, não calcula métricas
nem cria arquivos de avaliação ou resultados.

## evalute · Evaluate Results

Depois de gerar os casos, informe o diretório de uma execução do TCG
(o que contém `configs.md`) e o modelo de embeddings:

```bash
evalute --results-dir output/AAAA-MM-DD_HH-MM-SS \
  --embedding-model gemini-embedding-2
```

O avaliador usa a mesma `GOOGLE_API_KEY` do `.env`. O gabarito vem de
`data/normalized/`, ou do caminho indicado por `--data-dir`. A opção
`gemini-embedding-2` reproduz o modelo da v1. Também é possível escolher
`gemini-embedding-001`, com resultados dependentes do modelo.

O `evalute` lê os casos finais do TCG e compara com o gabarito por
similaridade cosseno, com limiar 0,70 e pareamento um a um. Grava
`results.json`, `results.csv` e `semantic_matches.json` em cada unidade
e `comparison.json` na raiz da execução. Os relatórios incluem precisão,
revocação, F1, pares, casos sem correspondência e uso de tokens quando
disponível. A comparação usa apenas unidades avaliáveis em comum entre
as soluções. Unidades com falha na geração ficam registradas sem avaliação.

Uma nova avaliação substitui os relatórios automáticos da mesma pasta.
Relatórios com revisão humana são protegidos. Os arquivos Markdown e o
gabarito original são preservados.
