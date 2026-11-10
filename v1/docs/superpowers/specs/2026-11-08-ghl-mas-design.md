# GHL-MAS — desenho do experimento

## Intenção

Criar uma ferramenta de pesquisa reprodutível para comparar One-shot, GHL e
Multiagent na geração de casos de teste de alto nível a partir de requisitos.
Ela não executa testes: compara semanticamente casos gerados com gabaritos
reservados, contabiliza uso e preserva artefatos auditáveis e revisão humana.

O primeiro ciclo abrange dados Firefox e E2EDev, os três geradores, avaliação
automática, persistência de execução e CLI de revisão humana.

## Objetivos

- Usar uma feature Firefox ou projeto E2EDev inteiro como unidade de trabalho.
- Enviar todos os requisitos e IDs da unidade em toda chamada de geração.
- Produzir casos estruturados: ID, título, descrição e IDs de requisito.
- Separar entrada de geração e gabarito até a fase de avaliação.
- Comparar soluções sob parâmetros, dados e modelos equivalentes.
- Preservar fontes, versões, decisões, custos, falhas e revisões.

## Não objetivos

- Executar cenários BDD, passos Python ou software dos datasets.
- Expor gabaritos a geradores, agentes de decisão ou prompts de cobertura.
- Alegar melhoria de modelo pela monotonicidade do estado Multiagent.
- Incluir Bluetooth, outros provedores ou datasets neste ciclo.

## Decisões confirmadas

- Python e Pydantic AI para integração Gemini, saídas Pydantic e uso reportado.
- Modelos de geração: `gemini-3.5-flash-lite` e `gemini-3.8-flash`.
- Embeddings exclusivamente com `gemini-embedding-2`.
- Credenciais ficam em ambiente/configuração local; `configs.md` nunca salva a chave.
- Dados brutos locais e imutáveis; JSON normalizado é fonte canônica.
- Firefox usa provisoriamente `R-nnn` → `TC-nnn`, com
  `inferred_row_alignment` e `pending_provenance_review`.
- `firefox_legacy` é o registro-pai imutável dos 184 pares. Geradores usam
  apenas as unidades-filhas de feature, definidas pela taxonomia determinística
  aprovada neste documento.
- E2EDev vem de commit fixado; somente requisitos e cenários BDD de
  `requirment_with_tests.json` participam do experimento.
- CLI de terminal usa `argparse`; fuso é `America/Recife`.

## Abordagens consideradas

1. **JSON normalizado mais fontes imutáveis — escolhida.** Transparente para
   textos longos, relações muitos-para-muitos, exclusões e proveniência.
2. **SQLite como fonte de verdade.** Facilita consultas, mas piora inspeção e diff.
3. **CSV/Parquet como fonte de verdade.** Ajuda análises tabulares, mas exige
   arquivos paralelos para textos longos e metadados.

## Dados locais

```text
data/
├── raw/
│   ├── firefox/{R-set.csv,T-set.csv}
│   └── e2edev/<commit>/
├── normalized/
│   ├── firefox_bookmarks.json
│   ├── e2edev_bench_01.json
│   └── manifests/{firefox_bookmarks,e2edev}.json
└── profiles/e2edev_coverage.json
```

`data/raw/` é excluído do Git por padrão. Manifestos registram URL, versão ou
commit, hash SHA-256, adaptador, itens excluídos, vínculos ambíguos e método de
obtenção. A normalização é determinística a partir de fonte e manifesto.

Cada JSON de unidade contém, em coleções separadas, requisitos e casos de
referência. Requisitos têm ID, texto integral, idioma e origem. Casos têm ID,
título, descrição, IDs de requisitos e metadados do vínculo. Exclusões e
ambiguidades permanecem explícitas no manifesto.

Firefox preserva os CSVs sem edição e gera o registro-pai `firefox_legacy`,
com 184 requisitos e 184 testes. Esse registro não é uma unidade de geração.
O adaptador gera as unidades-filhas abaixo, enviadas isoladamente aos geradores:

| Unidade | Requisitos |
| --- | --- |
| `firefox_bookmarks` | R-001–R-018 |
| `firefox_clipboard_and_drag_drop` | R-019–R-037 |
| `firefox_form_manager` | R-038–R-045 |
| `firefox_help` | R-046–R-072 |
| `firefox_browser_history` | R-073–R-084 |
| `firefox_image_and_embedded_content` | R-085–R-101 |
| `firefox_password_manager` | R-102–R-108 |
| `firefox_printing` | R-109–R-131 |
| `firefox_media_plugins` | R-132–R-134 |
| `firefox_search` | R-135–R-139 |
| `firefox_text_selection` | R-140–R-143 |
| `firefox_sidebar` | R-144–R-165 |
| `firefox_web_location` | R-166–R-174 |
| `firefox_themes` | R-175–R-181 |
| `firefox_toolbar` | R-182–R-184 |

Os intervalos e nomes pertencem à versão da taxonomia no manifesto. A regra é
determinística, baseada nos blocos contíguos e vocabulário do requisito,
verificada contra o teste associado. Casos transversais mantêm uma unidade
primária e podem ter etiquetas secundárias de domínio; não são copiados para
outras unidades, não duplicam casos de referência e não alteram a associação
provisória R-nnn → TC-nnn. Uma revisão posterior de procedência pode corrigir a
taxonomia, produzindo uma nova versão de dados.

E2EDev cria uma unidade por projeto/benchmark e extrai Gherkin para título e
descrição, excluindo código-fonte e passos Python.

A preparação valida uma unidade Firefox e uma E2EDev antes da carga completa.
No E2EDev inteiro, calcula cenários por requisito, incluindo zero; vínculos
múltiplos contam uma vez por requisito. Salva tabela, histograma, mediana e
quartis. Agentes recebem somente perfil agregado de calibração, nunca contagem
específica da unidade avaliada.

## Modelos e fronteiras

`schemas.py` define `Requirement`, `ReferenceCase`, `GeneratedCase`,
`GenerationResult`, `AgentOpinion`, `CandidateAssessment`, `UsageRecord`,
`SemanticMatch`, `EvaluationResult` e `HumanEvaluation`. IDs de saída são
validados contra a unidade antes de aceitação.

Dataset entrega `GenerationInput` sem gabarito; avaliação lê referência
independentemente. Uma fábrica Pydantic AI cria o modelo Gemini selecionado,
obtém credencial local, exige saída estruturada e registra tokens de entrada,
saída e detalhes disponíveis. Uso ausente é `unavailable`, nunca zero.

Antes de cada chamada, uma estimativa registra requisitos, instruções, histórico
e saída. Lote, por requisito e caso a caso variam apenas a saída pedida; todos
recebem requisitos completos. Se não couberem depois de reduzir histórico, a
unidade é incompatível ou usa modelo adequado, sem truncamento.

## Soluções

As três recebem a mesma entrada e produzem a mesma saída e texto canônico.

- **One-shot:** uma chamada por unidade para casos associados aos IDs.
- **GHL:** seleciona técnicas com todos os requisitos, a partir de catálogo
  inspirado na ISO/IEC/IEEE 29119-4:2021, gera por técnica reenviando o conjunto
  completo e consolida casos válidos. Essas regras são adaptação experimental do
  fluxo de Masuda et al.
- **Multiagent:** orquestrador Python determinístico mantém estado e chama
  analista, gerador, crítico, validador e cobertura em arquivos separados.
  Orquestrador e gerador são obrigatórios; os demais são opcionais na CLI.

Crítico ou validador abre uma rodada limitada por constante. Cada rodada produz
exatamente três tentativas independentes a partir dos requisitos, melhor estado
aceito e feedback. O analista só é refeito se habilitado. Cada tentativa passa
pelos controles até o solicitante; pedido do validador também passa pelo crítico,
se habilitado. Pareceres não abrem loops aninhados.

A seleção descarta inválidos e ordena por menos bloqueantes confirmados, mais
requisitos com casos válidos/distintos e menos duplicatas. Empates preservam o
estado aceito. Persistindo empate, rubrica comum compara tentativas e estado
anterior, registra justificativa e marca decisão qualitativa. Gabarito e
precision/recall/F1 não participam da decisão de agentes.

O estado Multiagent persiste análise, saída inicial, tentativas, pareceres,
escores, decisões, falhas e uso. Histórico no prompt pode ser resumido; versões
completas permanecem em disco. Cobertura recebe índice de aceitos/rejeitados e
perfil permitido para identificar lacunas, excesso e repetição.

## Avaliação automática

`gemini-embedding-2` produz embeddings com cache por modelo/versão e texto
canônico. Uso de embeddings fica separado do custo de geração. O limiar é
cosseno bruto `>= 0.70`, sem arredondamento nem opção de CLI.

O pareamento por unidade é bipartido um-a-um: maximiza primeiro o número de
pares elegíveis e, depois, a soma das similaridades. Persiste pares, IDs,
similaridade, textos/referências estáveis e não correspondências.

Com gabarito, `precision = pares / gerados`, `recall = pares / referências`
e F1 é a média harmônica. Saída vazia registra zero. Sem gabarito, status é
`not_evaluable` e métricas são vazias. O agregado usa totais e o mesmo conjunto
de unidades avaliáveis em cada solução.

## Revisão humana

`human_review.py` não chama modelos. Seleciona execução, solução e unidade;
mostra somente pares automáticos positivos, em ordem aleatória determinística,
ocultando similaridade e solução. Para cada par exibe requisito, referência e
gerado, recebendo `equivalent`, `different` ou `inconclusive` e justificativa.

Equivalentes confirmados recebem crédito. Denominadores permanecem totais de
gerados e referências; inconclusivos são separados e sem crédito. O resultado
declara `scope: automatic_matches_only`, pois não mede falsos negativos.

Revisão concluída oferece reavaliar ou cancelar. Cancelar não escreve. Ao
concluir reavaliação, a revisão anterior vai para `human_evaluation_history`,
a nova para `human_evaluation` e `results.json` é substituído atomicamente.

## CLI e resultados

`main.py` declara limiar, embeddings, três tentativas, limite de rodadas,
caminhos, fuso, modelos e modos. Comandos preparam dados e executam experimentos.
Execução seleciona modelo, unidades, soluções e agentes opcionais Multiagent.

Cada execução reserva atomicamente `results/YYYY-MM-DD_HH-MM-SS`. Em colisão,
aguarda o próximo segundo antes de chamadas e registra hora efetiva.

```text
results/<timestamp>/
├── configs.md
└── <solution>/
    ├── requirements_to_tests.md
    └── <unit_id>/
        ├── <requirement_id>/requirement.md
        ├── <requirement_id>/test cases/<sequence>_<safe-title>.md
        ├── intermediate/
        ├── semantic_matches.json
        ├── results.csv
        └── results.json
```

Pastas de requisitos existem sem casos. `requirements_to_tests.md` não duplica
caso por múltiplos vínculos. CSV tem linha por unidade com métricas, status,
contagens, tokens e embeddings. JSON preserva registro automático e adiciona
revisão humana. Falhas são parciais e preservam artefatos existentes.

`configs.md` registra parâmetros efetivos/padrão, versões de Python, Pydantic
AI, SDK Google, prompts e adaptadores, modelos, estado da credencial, fuso,
hashes de dados e situação final.

## Verificação e aceite

- Adaptadores verificam IDs, textos, origem, separação de gabarito, 184 vínculos
  Firefox inferidos, 15 unidades-filhas sem sobreposição e perfil E2EDev
  reproduzível.
- Modelos falsos exercitam IDs inválidos, One-shot, GHL, agentes desligados e
  retornos de crítico/validador com três tentativas e decisão persistida.
- Avaliação cobre valores abaixo, iguais e acima de 0,70, duplicatas, saída vazia,
  ausência de gabarito e pareamento um-a-um.
- Persistência cobre colisão, erro parcial, escrita atômica, cancelamento e
  reavaliação humana.
- Repetições criam diretórios independentes e permitem reconstruir vínculos,
  configuração, consumo, tentativas e métricas.

## Próximo passo

Após aprovação deste desenho, o plano de implementação definirá arquivos,
dependências, ordem de entrega, commit E2EDev e validação da estrutura Mendeley.
