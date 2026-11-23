# Ablation experiments

Each directory removes exactly one optional Multiagent agent from the
complete-agent reference configuration. Compare its evaluated metrics against
`../model-improvements/06_deterministic-revisions_reference/`.

- `no-analyst`: Analyst omitted; completed run.
- `no-critic`: Critic omitted; completed run.
- `no-validator`: Validator omitted; the consolidated run combines complete
  artifacts produced in separate provider-limited executions.
- `no-coverage`: Coverage omitted; currently incomplete until all eight units
  have generated successfully and are consolidated.

## Meaning of `consolidated`

A `consolidated` directory is an evaluable, synthetic run assembled from
multiple partial runs that share the same experimental configuration. It
contains one `configs.md` and all eight final unit artifacts. Evaluate this
directory, not the individual partial source runs.
