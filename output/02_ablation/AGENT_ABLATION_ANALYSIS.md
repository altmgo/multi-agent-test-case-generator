# Effect of Removing Multiagent Pipeline Agents

## Scope and reference

This report compares four single-agent ablations with the complete-agent
reference run in `../01_model-improvements/06_deterministic-revisions_reference/`.
Every comparison uses the same eight benchmark units, the
`gemini-3.5-flash-lite` model, `per_requirement` output mode,
`gemini-embedding-2` evaluation, and a similarity threshold of 0.70.

The complete-agent reference enables Analyst, Critic, Validator, and Coverage.
It generated 115 cases, matched 98 of 104 references, and obtained precision
0.8522, recall 0.9423, and F1 0.8950.

Each ablation is one stochastic model run. The results are evidence of the
observed trade-offs, not proof of a causal effect size without repeated runs.

## Aggregate results

| Configuration | Removed agent | Generated | Matched | Precision | Recall | F1 | Delta F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Complete reference | — | 115 | 98 | 0.8522 | 0.9423 | 0.8950 | — |
| No Analyst | Analyst | 95 | 87 | 0.9158 | 0.8365 | 0.8744 | -0.0206 |
| No Critic | Critic | 114 | 93 | 0.8158 | 0.8942 | 0.8532 | -0.0418 |
| No Validator | Validator | 107 | 95 | 0.8879 | 0.9135 | 0.9005 | +0.0055 |
| No Coverage | Coverage | 114 | 95 | 0.8333 | 0.9135 | 0.8716 | -0.0234 |

All five configurations evaluated all eight units, so unit coverage is 1.0 in
every row.

## Metric movement relative to the complete reference

| Removed agent | Generated cases | Matched references | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Analyst | -20 | -11 | +0.0636 | -0.1058 | -0.0206 |
| Critic | -1 | -5 | -0.0364 | -0.0481 | -0.0418 |
| Validator | -8 | -3 | +0.0357 | -0.0288 | +0.0055 |
| Coverage | -1 | -3 | -0.0188 | -0.0288 | -0.0234 |

## Interpretation by agent

### Analyst — primary coverage driver

Removing the Analyst produced the largest recall loss: 0.9423 to 0.8365.
The run generated 20 fewer cases and matched 11 fewer references, while
precision increased. This precision-recall split indicates that the Analyst
mainly supplies breadth: its explicit requirement-behavior inventory helps the
Generator identify distinct behaviors, rather than merely adding speculative
cases.

### Critic — strongest quality and revision control

Removing the Critic caused the largest F1 decrease, from 0.8950 to 0.8532.
Both precision and recall declined, despite generating nearly the same number
of cases as the complete reference. The Critic-free traces also contain zero
revision rounds: without the Critic checkpoint, neither model Critic feedback
nor the deterministic Critic fallback can initiate a revision. The observed
effect is consistent with the Critic improving both case selection and
explicit-scenario coverage.

### Validator — observed precision-recall trade-off

The no-Validator run generated eight fewer cases. Precision rose to 0.8879,
while recall fell to 0.9135. Its F1, 0.9005, is 0.0055 above the complete
reference in this single run.

This does **not** establish that the Validator is harmful. The improvement is
small, while the loss of three matched references shows a real coverage cost.
Because generation is stochastic, this result should be replicated before
changing the pipeline. The safe conclusion is that the Validator imposes a
conservative precision-versus-recall trade-off in this sample.

### Coverage — advisory stage with no direct revision path

Removing Coverage reduced F1 to 0.8716, through lower precision and recall.
However, Coverage is executed only after the accepted candidate has been
chosen and records an advisory report; it does not feed a revision request
back into the current orchestration loop. Consequently, this one-run metric
difference cannot be interpreted as a direct effect of a Coverage-driven
revision. It is primarily evidence that the overall stochastic run was weaker;
repeated paired runs would be needed to estimate any indirect effect reliably.

## Overall conclusion

The observed ablations support retaining Analyst and Critic:

- **Analyst** is most important for recall and behavioral coverage.
- **Critic** is most important for overall quality and is required for the
  verified revision path.
- **Validator** has the most ambiguous result: it traded recall for precision,
  with a marginally higher single-run F1 when omitted.
- **Coverage** should be described as an advisory reporting stage in the
  current implementation, not as a generator/revision control, unless its
  output is later connected to a revision decision.

The recommended reference for future agent-removal comparisons remains the
complete deterministic-revisions run, because it is the configuration where
the revision mechanism was observed end to end.

## Source comparisons

- `2026-11-22_ablation-no-analyst/2026-11-22_22-06-58/comparison.json`
- `2026-11-22_ablation-no-critic/2026-11-22_22-16-23/comparison.json`
- `2026-11-23_ablation-no-validator/2026-11-23_09-58-41/comparison.json`
- `2026-11-23_ablation-no-coverage/2026-11-23_19-57-28/comparison.json`
- `../01_model-improvements/06_deterministic-revisions_reference/2026-11-22_problem4-deterministic-revisions-v4/2026-11-22_21-44-24/comparison.json`
