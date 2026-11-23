# Chronology of Multiagent Model Improvements

## Purpose and scope

This document explains how the Multiagent generator evolved from 20 to 22
November. It records the question addressed by each experiment, the change
tested, the observed metrics, and whether that change was retained, reverted,
or used as the reference configuration for ablations.

All six stages used the same benchmark scope: eight units (`e2edev_bench_01`
through `e2edev_bench_04`, `firefox_bookmarks`, `firefox_browser_history`,
`firefox_password_manager`, and `firefox_themes`), the
`gemini-3.5-flash-lite` model, all four optional agents, and
`per_requirement` output mode. This shared setup makes the metric trend useful
for interpreting the experiments, while each run remains a stochastic model
generation.

## At a glance

| Stage | Date | Change under test | Generated | Matches | Precision | Recall | F1 | Decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 01 | 20 Nov | Expand explicit scenario types | 177 | 95 | 0.5367 | 0.9135 | 0.6762 | Superseded |
| 02 | 20 Nov | Ground generation in requirement text | 86 | 82 | 0.9535 | 0.7885 | 0.8632 | Retained |
| 03 | 22 Nov | Enumerate atomic explicit behaviors | 107 | 97 | 0.9065 | 0.9327 | 0.9194 | Retained; best F1 |
| 04 | 22 Nov | Add merge and deduplication guidance | 114 | 98 | 0.8596 | 0.9423 | 0.8991 | Reverted |
| 05a | 22 Nov | Make Critic inspect explicit scenario gaps | 114 | 96 | 0.8421 | 0.9231 | 0.8807 | Not validated |
| 05b | 22 Nov | Complete rerun of Critic-coverage implementation | 119 | 97 | 0.8151 | 0.9327 | 0.8700 | Not validated |
| 06 | 22 Nov | Deterministic revision fallback | 115 | 98 | 0.8522 | 0.9423 | 0.8950 | Ablation reference |

`Matches` is the number of generated cases semantically matched one-to-one
with the 104 reference cases. Precision measures how many generated cases
matched a reference; recall measures how many reference cases were matched.

## Stage 01 — Recall expansion

**Folder:** `01_recall-expansion_superseded/2026-11-20_21-16-16/`

The first improvement removed the previous limit of two focused cases per
requirement. The Analyst enumerated Normal, Edge, Boundary, and Error or
Abnormal scenario types; the Generator was asked to generate each distinct
type supported by a requirement; Critic and Coverage prompts were expanded to
look for missing variants.

The change solved undergeneration: recall rose to 0.9135. It also caused
substantial overgeneration, especially for simple Firefox requirements. The
run produced 177 cases for 104 references, reducing precision to 0.5367 and
F1 to 0.6762. The strategy was therefore superseded rather than kept as the
final behavior.

## Stage 02 — Precision calibration

**Folder:** `02_precision-calibration_retained/2026-11-20_21-49-30/`

This stage addressed the overgeneration of Stage 01. Prompts required every
case to be grounded in the written requirement, prohibited speculative
conditions, and treated simple declarative requirements as one focused normal
case. The Analyst was instructed to list alternative scenario types only when
the requirement explicitly described them; Critic and Coverage were instructed
to flag excess and unsupported cases.

Precision recovered from 0.5367 to 0.9535. Recall decreased to 0.7885, but
the resulting F1 of 0.8632 was the best result at that point. This grounding
and atomicity calibration was retained as the foundation for later coverage
work.

## Stage 03 — Atomic coverage

**Folder:** `03_atomic-coverage_retained/2026-11-22_atomic-coverage-v1/`

The next hypothesis was that recall could increase again without reviving the
speculation problem. Analyst and Generator prompts were strengthened to
identify concrete atomic actions, state transitions, persistence operations,
visibility changes, and explicitly stated error conditions. The Generator was
asked to map each such explicit behavior to a focused case.

This was the strongest metric run: 97 of 104 references matched, with recall
0.9327 and F1 0.9194. Precision remained high at 0.9065. The experiment is
retained because it improved coverage while preserving the grounding principle
from Stage 02.

## Stage 04 — Deduplication and grounding refinement

**Folder:** `04_dedup-grounding_reverted/2026-11-22_dedup-grounding-v2/`

This experiment attempted to remove extra cases from Stage 03 by adding
stricter merge and deduplication directions to Generator and Critic. It gained
one matched reference and raised recall slightly to 0.9423, but generated even
more cases: 114 instead of 107. Precision fell to 0.8596 and F1 fell to
0.8991.

Because the added deduplication guidance made the aggregate result worse, it
was reverted. The earlier atomic-coverage behavior remained the preferred
metric configuration.

## Stage 05 — Critic explicit-scenario coverage

**Folder:** `05_critic-coverage_not-validated/`

The Critic was changed to compare every requirement with explicitly described
scenarios, identify missing scenarios as actionable gaps, and request a
revision when such gaps existed. Candidate selection was also adjusted to
reward valid, distinct cases.

Two complete runs are retained here:

- **v1** produced F1 0.8807.
- **v3** was a complete rerun after an incomplete v2 provider-limited run and
  produced F1 0.8700.

Neither v1 nor v3 created a Critic-initiated revision round: initial opinions
returned `request_revision=false` for all eight units. Consequently, the
intended behavioral effect was not demonstrated and both runs are classified
as not validated. They remain important evidence that prompt-only Critic
guidance was insufficient to reliably trigger revisions.

## Stage 06 — Deterministic revision fallback

**Folder:** `06_deterministic-revisions_reference/2026-11-22_problem4-deterministic-revisions-v4/`

Stage 06 addressed the failure mode found in Stage 05. Instead of relying only
on model opinions, the orchestrator deterministically compares each
requirement and its linked cases for explicitly paired behaviors, such as
add/delete, select/deselect, valid/invalid, empty/restored, and
single/multiple. A missing pair or an unlinked requirement replaces the Critic
opinion with an actionable revision request.

The run demonstrated the intended control flow: `e2edev_bench_03` created one
revision round, generated three candidates, and selected
`round-1-candidate-3` to address a missing deselection scenario. The aggregate
F1 was 0.8950, below Stage 03's best F1, but recall reached 0.9423 and the
revision mechanism was demonstrably active.

This is the **complete-agent reference for ablations**. It was selected not
because it had the best F1, but because it is the version whose revision
mechanism was verified end to end. Agent-removal experiments should be
compared with this stage.

## How to interpret the decisions

- Use **Stage 03** when reporting the strongest observed quality metric.
- Use **Stage 06** when discussing the final system behavior and the ablation
  study, because it includes verified deterministic revision control.
- Treat **Stages 01, 04, and 05** as negative or inconclusive evidence, not
  as regressions to delete: they justify the later design choices.
- Keep the original `configs.md`, traces, generated cases, and evaluation
  files in every run directory as the reproducibility record behind this
  chronology.
