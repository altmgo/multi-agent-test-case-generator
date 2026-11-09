# Separate Evaluation CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `ghl-mas run` generation-only and add `ghl-mas-evaluate` to evaluate or re-evaluate persisted runs in place.

**Architecture:** Generation continues to publish the complete immutable case snapshot, now with status `generated` and no embedding call. A new `evaluation_cli.py` reconstructs `Unit` and `GeneratedCase` objects from those snapshots, evaluates selected artifacts, and uses a narrow persistence function to atomically replace each derived file while retaining generation and human-review fields. After each invocation it rebuilds run-wide configuration and comparison state from every persisted unit, not only the selected filter.

**Tech Stack:** Python 3.11+, argparse, Pydantic, existing Gemini embedder/evaluation/persistence modules, pytest.

**Spec:** `docs/superpowers/specs/2026-11-09-separate-evaluation-cli-design.md`

## Global Constraints

- Add no dependency, service, artifact schema version, or output directory.
- Evaluation reads only persisted run snapshots; it never regenerates cases or reads normalized datasets.
- Update the selected run in place with atomic file replacement and preserve generation, intermediate, Markdown, and human-review data.
- `--run` is required; `--solution` and `--unit` are optional filters; an unfiltered invocation evaluates every eligible artifact.
- A filtered invocation rebuilds comparison/configuration from all currently finalized evaluations in the run.
- Continue after unit-level embedding failures and allow a later invocation to repair them.

## Review Focus

- A run name or snapshot path attempting traversal or using a symlink must be rejected before embedding or writes; covered by Task 2 selection tests.
- A malformed or internally inconsistent snapshot must remain byte-for-byte unchanged; covered by Task 2 validation tests.
- A generation-stage failure must not be misclassified as retryable evaluation work; covered by Task 2 eligibility tests.
- Re-evaluation concurrent with human-review publication must fail cleanly instead of losing either writer's data; covered by Task 2 locking test.
- A filtered retry must retain unselected metrics and human-review fields while rebuilding the common-unit comparison; covered by Task 2 filtered retry test.

---

### Task 1: Publish Generation-Only Runs

**Files:**
- Modify: `tests/test_run.py:120-240,305-314,424-602`
- Modify: `main.py:17-18,80-83,245-299,316-421`
- Modify: `persistence.py:196-260`

**Interfaces:**
- Consumes: Existing `GenerationResult`, generation failures, `save_unit`, solution index, and run configuration.
- Produces: `save_unit(run, solution, unit, result, None, *, failure=...)` where no evaluation and no failure publishes status `generated`; `ghl-mas run` never constructs an embedder or writes `comparison.json`.

- [ ] **Step 1: Write failing generation-lifecycle tests**

Update `tests/test_run.py` so the successful-run test replaces `make_embedder` with a function that fails if called and asserts: unit `status == "generated"`, `failure is None`, `evaluation is None`, embedding requests are zero, the CSV/match artifacts have status `generated`, `comparison.json` is absent, the config outcome is `generated`, and top-level config status is `generated`. Retain assertions for generation failures, interruptions, indexes, immutable case files, and secret redaction; remove evaluation-only assertions from this suite.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `pytest tests/test_run.py -q`

Expected: FAIL because `main._execute` calls the embedder and `save_unit` rejects a success without an evaluation.

- [ ] **Step 3: Extend `save_unit` with the generated state**

In `persistence.py`, keep the existing signature and validation, but accept exactly three valid outcomes: generated (`evaluation is None`, `failure is None`), failed (`evaluation is None`, `failure` present), or finalized (`evaluation` present, `failure is None`). Publish generated snapshots with null evaluation/failure, zero embedding requests, and generated status in JSON, CSV, and semantic matches.

- [ ] **Step 4: Remove evaluation from `main._execute`**

Delete embedding/evaluation construction and aggregation from `main.py`; save every successful `GenerationResult` as generated, omit `comparison.json`, record generated outcomes, and return success when every generation and solution index succeeds. Keep failure continuation, cancellation behavior, and config finalization intact; use top-level `generated`, `partial`, `failed`, or `interrupted` status as applicable.

- [ ] **Step 5: Run focused and persistence tests and verify GREEN**

Run: `pytest tests/test_run.py tests/test_human_review.py -q`

Expected: PASS, with review tests still accepting only finalized automatic evaluations.

- [ ] **Step 6: Commit the generation-only lifecycle**

```bash
git add main.py persistence.py tests/test_run.py
git commit -m "refactor: separate evaluation from generation"
```

### Task 2: Evaluate Persisted Runs In Place

**Files:**
- Create: `evaluation_cli.py`
- Create: `tests/test_evaluation_cli.py`
- Modify: `persistence.py:147-174,196-260`
- Modify: `pyproject.toml:17-25`

**Interfaces:**
- Consumes: Persisted schema-version-1 `results.json`, `evaluation.metrics.evaluate`, `main.make_embedder`, `persistence.write_json`, and `evaluation.metrics.aggregate`.
- Produces: `persistence.update_evaluation(path: Path, expected: bytes, evaluation: EvaluationResult | None, *, failure: dict[str, str] | None = None, embedding_usage: UsageRecord | None = None, embedding_requests: int | None = None) -> None`; `evaluation_cli.make_embedder() -> Embedder`; `evaluation_cli.evaluate_run(run: Path, solution: str | None = None, unit_id: str | None = None) -> int`; `evaluation_cli.main(argv: list[str] | None = None) -> int`; console entry point `ghl-mas-evaluate`.

- [ ] **Step 1: Write failing happy-path and retry tests**

Create `tests/test_evaluation_cli.py` with persisted generated fixtures using real `save_unit` and a fake embedder. Assert that `main(["--results-dir", ..., "--run", RUN])` evaluates all eligible solution/unit snapshots, updates JSON/CSV/semantic matches in the same directories, writes `comparison.json`, changes config outcomes to `evaluated` or `not_evaluable`, and ends `completed`. Add a retry case starting from an old `failure.stage == "evaluation"` snapshot and assert it becomes evaluated without changing generated cases, generation usage, intermediate links, or `human_evaluation`/history.

- [ ] **Step 2: Run happy-path tests and verify RED**

Run: `pytest tests/test_evaluation_cli.py -q`

Expected: collection FAIL because `evaluation_cli` and `persistence.update_evaluation` do not exist.

- [ ] **Step 3: Implement validated snapshot loading and selection**

In `evaluation_cli.py`, define a private Pydantic snapshot model for schema version, solution, unit ID, parent ID, requirements, generated cases, reference cases, status, failure, and evaluation. Resolve `<results-dir>/<run>` without accepting absolute names, traversal, symlinks, unknown solutions/units, duplicate unit IDs, unsupported schemas, inconsistent links/counts, generation failures, or malformed JSON. Treat statuses `generated`, `evaluated`, `not_evaluable`, and failures whose stage is `evaluation` as eligible; match solution names case-insensitively.

- [ ] **Step 4: Implement atomic derived-artifact publication**

In `persistence.update_evaluation`, acquire the same nonblocking unit-directory `flock` used by human review, compare the locked snapshot bytes with `expected`, merge only `status`, `failure`, `evaluation`, and embedding usage/request fields, and preserve all unknown and human-review keys. Reuse `_write_csv` and the semantic-match payload shape; write CSV and semantic matches atomically, then write `results.json` last as the commit marker. Reject simultaneous writers or a changed snapshot.

- [ ] **Step 5: Implement evaluation execution and run-wide aggregation**

In `evaluation_cli.evaluate_run`, reuse one embedder per invocation, continue across per-unit `EmbeddingError`/unexpected failures, persist sanitized failure type and known usage, and close the embedder in `finally`. After selected work, load every finalized evaluation in the run, aggregate by every configured solution and unit, atomically replace `comparison.json`, and update config outcomes/status/comparison. Return `1` only when selected work fails; a successful filtered evaluation returns `0` while the config remains `partial` until all eligible artifacts are finalized.

- [ ] **Step 6: Add selection, safety, failure, and concurrency tests**

Add tests asserting: optional solution/unit filters touch only selected snapshots but retain all finalized units in comparison; unknown/traversal/symlink selectors perform no request/write; malformed snapshots remain unchanged; generation failures are skipped and keep the run partial; one embedding failure does not stop later units and a subsequent retry repairs it; provider secrets never reach files/stderr; and a held unit-directory lock makes publication fail without changing artifacts.

- [ ] **Step 7: Add the CLI parser and package entry point**

Implement argparse options `--results-dir` (default `results`), required `--run`, optional `--solution`, and optional `--unit`; print per-unit failures without provider detail and a concise final result. Register `ghl-mas-evaluate = "evaluation_cli:main"` and include `evaluation_cli` in `py-modules`.

- [ ] **Step 8: Run evaluation tests and verify GREEN**

Run: `pytest tests/test_evaluation_cli.py tests/test_evaluation.py tests/test_human_review.py -q`

Expected: PASS.

- [ ] **Step 9: Commit the evaluation CLI**

```bash
git add evaluation_cli.py persistence.py pyproject.toml tests/test_evaluation_cli.py
git commit -m "feat: add standalone evaluation CLI"
```

### Task 3: Exercise and Document the Three-Stage Workflow

**Files:**
- Modify: `tests/test_integration.py:89-168`
- Modify: `README.md:61-165`

**Interfaces:**
- Consumes: `main.main`, `evaluation_cli.main`, `human_review.main`, and their persisted artifact contract.
- Produces: Documented and integration-tested `run -> evaluate -> review` workflow.

- [ ] **Step 1: Write the failing end-to-end workflow test**

Change the integration test to call `ghl-mas run`, assert every successful snapshot is generated and no comparison exists, invoke `evaluation_cli.main` for that run, assert automatic metrics/comparison, then perform review and rereview. Keep assertions that evaluation leaves generation artifacts intact and review leaves automatic CSV/comparison intact.

- [ ] **Step 2: Run the integration test and verify RED**

Run: `pytest tests/test_integration.py -q`

Expected: FAIL until the integration fixture patches the embedder in `evaluation_cli` and invokes the new phase.

- [ ] **Step 3: Complete the integration fixture and README**

Patch the fake embedder at the new ownership boundary. In `README.md`, separate generation from automatic evaluation, show `ghl-mas-evaluate --run "${RUN##*/}"`, document optional `--solution`/`--unit`, in-place retries and failure continuation, explain that `comparison.json` appears after evaluation, and present review as the final optional stage.

- [ ] **Step 4: Run the integration test and verify GREEN**

Run: `pytest tests/test_integration.py -q`

Expected: PASS for prepared fixtures; the prepared-real-units parameter may SKIP only when local data is absent.

- [ ] **Step 5: Run the full suite**

Run: `pytest -q`

Expected: PASS with only the pre-existing conditional local-data skip.

- [ ] **Step 6: Commit documentation and integration coverage**

```bash
git add README.md tests/test_integration.py docs/superpowers/specs/2026-11-09-separate-evaluation-cli-design.md docs/superpowers/plans/2026-11-09-separate-evaluation-cli.md
git commit -m "docs: describe separate evaluation workflow"
```
