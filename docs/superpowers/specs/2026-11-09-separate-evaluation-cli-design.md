# Separate Evaluation CLI Design

## Intent

Separate expensive, retryable semantic evaluation from generation. `ghl-mas run` must only generate and persist cases; `ghl-mas-evaluate` must evaluate an existing run in place; `ghl-mas-review` remains the human-review step.

## Goals

- Publish generated unit artifacts without calling the embedding API.
- Add `ghl-mas-evaluate --run <timestamp>` with optional `--solution` and `--unit` filters.
- Reconstruct evaluation inputs exclusively from the selected run's persisted snapshots.
- Atomically replace automatic evaluation fields and derived CSV/match/config/comparison artifacts in the same run directory.
- Preserve generation data, intermediate traces, Markdown case files, and any human evaluation history.
- Continue after per-unit embedding failures and make a later rerun repair them.
- Document the `run -> evaluate -> review` workflow in `README.md`.

## Non-goals and constraints

- No new dependency, service, artifact schema version, or output directory.
- Evaluation does not regenerate cases or read mutable normalized datasets.
- A filtered evaluation updates selected units and then rebuilds the run-wide comparison from every currently evaluated unit.
- Unsafe paths, malformed snapshots, and ambiguous unit IDs are rejected before writes.

## Approaches

1. **Separate executable, in-place update (selected).** Add the `ghl-mas-evaluate` entry point, matching `ghl-mas-review`; explicitly select a run and update it atomically. This keeps the three lifecycle stages visible and makes retries cheap.
2. **`ghl-mas evaluate` subcommand.** Smaller packaging change, but rejected because evaluation should be operationally separate like review.
3. **Automatically evaluate the newest run.** Shorter invocation, but rejected because it can mutate the wrong experiment.

## Artifact lifecycle

Generation snapshots use a generated state with no automatic evaluation. Evaluation replaces only automatic status, failure, embedding usage, `evaluation`, `semantic_matches.json`, and the evaluation columns in `results.csv`; it then refreshes `comparison.json` and evaluation outcome/config status. Human-review fields, when present, remain untouched.
