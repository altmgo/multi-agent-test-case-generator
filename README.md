# Ferramentas de pesquisa

As ferramentas usam os JSONs de `data/normalized/` que acompanham o repositório.
Rode os comandos abaixo a partir da raiz do repositório com Python 3.11 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Se o terminal estava com o ambiente ativo antes de mover o projeto,
abra um terminal novo antes de ativar a `.venv` da raiz.

Crie `.env` e defina a chave do provedor escolhido. A CLI lê o arquivo
no diretório atual e o Git ignora o arquivo.

## tcg · Test Case Generator

Use `GOOGLE_API_KEY` para os modelos Gemini ou `GROQ_API_KEY` para
`openai/gpt-oss-120b`. A opção `--model` determina o provedor e a chave.

```bash
tcg run \
  --model gemini-3.5-flash-lite \
  --solutions one-shot GHL Multiagent \
  --units firefox_bookmarks.json e2edev_bench_01.json \
  --agents analyst critic validator coverage \
  --output-mode batch
```

Para executar a mesma geração com Groq, use
`--model openai/gpt-oss-120b`. Os limites de uso da sua conta Groq se
aplicam a essa execução.

Para GPT-OSS 120B no Groq, a CLI espaça os envios em pelo menos dois segundos
e usa uma janela móvel de 60 segundos com orçamento local de 8.000 tokens.
Antes de enviar, reserva a entrada estimada e o limite de saída da chamada.
O modelo usa raciocínio baixo e reserva até 4.096 tokens para gerar casos
ou 1.536 para seleção, análise e pareceres. A CLI registra as esperas
preventivas. O limite da conta é compartilhado com outros processos.
Se os requisitos completos e o contexto obrigatório deixarem menos espaço
que a reserva mínima de saída, a CLI sinaliza a chamada como incompatível.

Para Groq e Gemini, cada chamada com erro da API ou resposta rejeitada pelo
Pydantic AI tem até três retentativas, além da tentativa inicial. O intervalo
base é de 2, 4 e 8 segundos, ou 15, 30 e 60 segundos se todas as falhas forem
por limite de taxa. Cada espera automática tem teto de 60 segundos.
Quando o provedor informa cota esgotada ou devolve limite de taxa com
`Retry-After` acima desse teto, a execução termina como parcial e preserva
as saídas já gravadas. A CLI mostra a unidade, a etapa, o erro, o tempo de
espera e o resultado da retentativa. Retentativas podem consumir tokens.

Omita `--units` para gerar a partir de todos os JSONs elegíveis de
`data/normalized/`. Os manifestos ficam fora da geração. Use o nome da unidade com `.json`,
como `firefox_bookmarks.json`. A CLI extrai os requisitos de cada arquivo e ignora
os casos de referência, inclusive na etapa de cobertura do Multiagent.

O GHL usa um catálogo fixo em `src/ghl/__init__.py`, inspirado no fluxo de
[Masuda et al.](https://arxiv.org/html/2510.03641v1#S3). O modelo escolhe as
técnicas aplicáveis a partir dos requisitos e do catálogo, depois gera casos
para cada técnica escolhida. As escolhas e justificativas ficam em `configs.md`.

Use `--output-dir` para escolher outro destino e `--data-dir` para indicar
outros JSONs normalizados. A pasta de cada execução segue o formato
`output/AAAA-MM-DD_HH-MM-SS/` no fuso `America/Recife`. Cada solução tem
`requirements_to_tests.md` e uma pasta por unidade, com `requirement.md`
e `test cases/*.md` por requisito. A execução registra a configuração em
`configs.md` e o Multiagent grava suas revisões em `intermediate/`.
A CLI gera casos com Gemini ou Groq. Não executa os casos, não calcula métricas
nem cria arquivos de avaliação ou resultados.

## evaluate · Evaluate Results

Depois de gerar os casos, informe o diretório de uma execução do TCG
(o que contém `configs.md`) e o modelo de embeddings:

```bash
evaluate --results-dir output/AAAA-MM-DD_HH-MM-SS \
  --embedding-model gemini-embedding-2
```

O avaliador usa `GOOGLE_API_KEY` do `.env`, inclusive para avaliar casos
gerados com Groq. O gabarito vem de
`data/normalized/`, ou do caminho indicado por `--data-dir`. A opção
`gemini-embedding-2` reproduz o modelo da v1. Também é possível escolher
`gemini-embedding-001`, com resultados dependentes do modelo.

O avaliador reaproveita embeddings idênticos durante a execução. Envia até
20 textos por lote, com pelo menos 2 segundos entre envios e um orçamento
local de 100 textos em uma janela móvel de 60 segundos. Os limites do Gemini
variam por modelo e projeto. Falhas transitórias têm até três retentativas
com espera crescente e teto de 60 segundos por espera. A CLI registra as
esperas e retentativas. Se o provedor informar cota diária esgotada, pedir
uma espera superior a 60 segundos em um HTTP 429 ou continuar devolvendo 429
até o fim das retentativas, o avaliador grava uma comparação parcial.

O `evaluate` lê os casos finais do TCG e compara com o gabarito por
similaridade cosseno, com limiar 0,70 e pareamento um a um. Grava
`results.json`, `results.csv` e `semantic_matches.json` em cada unidade
e `comparison.json` na raiz da execução. Os relatórios incluem precisão,
revocação, F1, pares, casos sem correspondência e uso de tokens quando
disponível. A comparação usa apenas unidades avaliáveis em comum entre
as soluções. Unidades com falha na geração ficam registradas sem avaliação.

Uma nova avaliação substitui os relatórios automáticos da mesma pasta.
Relatórios com revisão humana são protegidos. Os arquivos Markdown e o
gabarito original são preservados.
