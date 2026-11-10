# GHL-MAS

Experimento para comparar três formas de gerar casos de teste de alto nível a
partir de requisitos. One-shot faz uma chamada por unidade. GHL seleciona
técnicas e gera casos por técnica. Multiagent usa um orquestrador Python com
gerador obrigatório e agentes opcionais. A implementação de GHL adapta o
fluxo descrito por Masuda et al. [Artigo de referência](https://arxiv.org/html/2510.03641v1#S3)

## Instalação

No diretório do projeto, use Python 3.11 ou superior em um ambiente POSIX
com Bash e sistema de arquivos local.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
```

Os testes usam modelos e embeddings simulados. Se os dados normalizados
estiverem disponíveis localmente, o teste de integração também exercita
`firefox_bookmarks` e `e2edev_bench_01` reais com esses simuladores.

## Obtenção e preparação dos dados

**Firefox.** Obtenha os arquivos originais `R-set.csv` e `T-set.csv` e
salve-os em `data/raw/firefox/`. A preparação preserva os 184 pares em
`firefox_legacy` e cria 15 unidades de feature para geração. Os 184
vínculos `R-nnn` → `TC-nnn` são inferidos pelo alinhamento das linhas
e aguardam revisão de procedência. [Mendeley Data, versão 1, CC BY 4.0](https://data.mendeley.com/datasets/jw5bgshtvg/1)

```bash
mkdir -p data/raw/firefox
cp ~/Downloads/R-set.csv ~/Downloads/T-set.csv data/raw/firefox/
ghl-mas prepare firefox
```

**E2EDev.** Obtenha as anotações do commit fixado. A preparação verifica
o SHA-256 dos 46 arquivos de anotação esperados e usa o texto dos requisitos
e o Gherkin de `requirment_with_tests.json`. Cada benchmark forma uma
unidade. A licença do snapshot permanece sem verificação.
[Repositório E2EDev no commit utilizado](https://github.com/SCUNLP/E2EDev/tree/d280dd144fbff30c237af26c1a76948e2f8857fa)

```bash
E2EDEV_COMMIT=d280dd144fbff30c237af26c1a76948e2f8857fa
E2EDEV_RAW="data/raw/e2edev/$E2EDEV_COMMIT"
mkdir -p data/raw/e2edev
git clone --filter=blob:none --no-checkout https://github.com/SCUNLP/E2EDev.git "$E2EDEV_RAW"
git -C "$E2EDEV_RAW" sparse-checkout set --no-cone '/E2EDev_data/E2ESD_Bench_*/requirment_with_tests.json'
git -C "$E2EDEV_RAW" checkout --detach "$E2EDEV_COMMIT"
ghl-mas prepare e2edev
```

Os JSONs ficam em `data/normalized/`. Os manifestos registram fonte,
versão, hashes, adaptador e detalhes de vínculo ou exclusão. Os dados
brutos e normalizados acompanham o repositório. O preparo E2EDev também grava a
tabela de cenários por requisito, o histograma e o resumo descritivo em
`data/profiles/`, incluindo requisitos com zero cenários.

## Execução com Gemini

Configure uma chave da Gemini Developer API no ambiente da sessão. O
programa lê `GOOGLE_API_KEY` ou, como alternativa, `GEMINI_API_KEY`.
Os metadados da execução registram apenas o nome da variável e a presença
da credencial. [Chaves da API Gemini](https://ai.google.dev/gemini-api/docs/api-key)

```bash
read -rsp 'Chave Gemini: ' GOOGLE_API_KEY
printf '\n'
export GOOGLE_API_KEY

ghl-mas run \
  --model gemini-3.5-flash-lite \
  --solutions one-shot GHL Multiagent \
  --units firefox_bookmarks e2edev_bench_01 \
  --agents analyst critic validator coverage \
  --output-mode batch
```

`--model` também aceita `gemini-3.8-flash`. Use `--agents` sem nomes
para executar Multiagent apenas com o orquestrador e o gerador. Os modos
`batch`, `per_requirement` e `per_case` definem o escopo da saída de GHL
e Multiagent. One-shot sempre usa `batch`. Todas as soluções recebem os
requisitos completos da unidade. O gabarito da unidade avaliada entra
apenas na avaliação.

### Calibração opcional

Para testar a calibração do agente de cobertura, selecione unidades E2EDev
diferentes das unidades avaliadas. Apenas o agregado desse recorte
(contagem de requisitos, histograma e quartis) entra no agente de
cobertura do Multiagent para as unidades E2EDev. A execução registra os
IDs de calibração, hashes, versão e agregado em `configs.md`. O perfil
descritivo de todo o corpus serve para inspeção dos dados.

```bash
ghl-mas run \
  --model gemini-3.5-flash-lite \
  --solutions one-shot GHL Multiagent \
  --units firefox_bookmarks e2edev_bench_01 \
  --agents analyst critic validator coverage \
  --output-mode batch \
  --calibration-units e2edev_bench_02
```

## Resultados e revisão humana

Cada execução cria um diretório `results/AAAA-MM-DD_HH-MM-SS/` no fuso
`America/Recife` e imprime o caminho ao terminar. Consulte `configs.md`
para a configuração efetiva e `comparison.json` para a comparação entre
soluções. Cada pasta de solução contém `requirements_to_tests.md` e uma
pasta por unidade, com `results.json`, `results.csv`,
`semantic_matches.json`, casos em Markdown e artefatos intermediários
quando disponíveis.

```bash
ghl-mas-review
```

Selecione a execução, a solução e a unidade pelos menus. É possível
fixar seleções na linha de comando. Por exemplo, o comando abaixo usa
a execução mais recente no diretório padrão.

```bash
RUN=$(printf '%s\n' results/*/ | sort | tail -n 1)
RUN=${RUN%/}
ghl-mas-review --run "${RUN##*/}" --solution Multiagent --unit firefox_bookmarks
```

Durante o julgamento, a CLI apresenta apenas pares positivos da avaliação
automática em ordem embaralhada determinística. Cada par mostra os
requisitos vinculados, a referência e o caso gerado. A tela de julgamento
omite a solução, a similaridade e os IDs técnicos. A seleção anterior e o
estilo do texto ainda podem indicar a origem do caso.

Digite `equivalent`, `different` ou `inconclusive`. A justificativa é
opcional. Confirme a gravação com `y` ou cancele no prompt. Também é
possível cancelar com `q` nos menus e no julgamento ou encerrando a
entrada antes de confirmar. A revisão é local e dispensa credenciais.
Uma nova revisão confirmada arquiva a anterior em
`human_evaluation_history` e grava a atual em `human_evaluation`, com
data UTC e as decisões. Os resultados automáticos e os CSVs são
preservados. Unidades que falharam antes da avaliação ficam fora da fila.

## Interpretação e limites

- **Avaliação automática.** Usa `gemini-embedding-2`, cosseno bruto
  `>= 0.70` e pareamento um-a-um. Maximiza primeiro a quantidade de
  pares e depois a soma das similaridades. Similaridade semântica
  é uma aproximação de equivalência funcional. O experimento mede
  correspondência textual e mantém os cenários e o software sem execução.
- **Métricas humanas.** O escopo `automatic_matches_only` cobre
  somente os pares encontrados pela avaliação automática. Apenas os
  equivalentes recebem crédito. Os denominadores continuam sendo todos
  os casos gerados e todas as referências. Os inconclusivos são contados
  separadamente e recebem zero crédito. A revisão não estima falsos
  negativos entre pares que ficaram de fora.
- **Unidades e comparação.** Com gabarito e zero pares, as métricas
  são zero. Sem gabarito, ficam nulas. A comparação automática agrega
  as contagens da interseção de unidades avaliáveis das soluções e
  informa sua cobertura. Os vínculos inferidos do Firefox afetam a
  interpretação dos resultados. A calibração opcional altera a
  configuração do Multiagent para E2EDev e deve constar da comparação.
- **Uso do provedor.** Tokens de geração e embeddings ficam em campos
  separados. Contadores omitidos pelo provedor ficam ausentes ou
  parciais, e valores monetários de cobrança ficam indisponíveis. O
  cache de embeddings é local à execução e pode reduzir a quantidade
  de chamadas.
