# Embedding Rate-Limit Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `ghl-mas-evaluate` finish large Gemini embedding evaluations by batching 20 inputs and retrying only HTTP 429 responses after 15, 30, and 60 seconds.

**Architecture:** Keep fallback inside `GeminiEmbedder`, below the evaluation CLI, so every evaluation uses the same cache, usage accounting, validation, and redaction. Each batch gets one initial request plus three bounded 429 retries; successful batches continue normally and all attempts contribute to request/usage totals.

**Tech Stack:** Python 3.11+, google-genai 3.0.0, existing `EmbeddingBatch`/`EmbeddingError`, pytest/httpx mock transport.

**Spec:** `docs/superpowers/specs/2026-11-09-embedding-rate-limit-fallback-design.md`

## Global Constraints

- Use batches of exactly at most 20 canonical texts.
- Retry only HTTP 429, with delays of exactly 15, 30, and 60 seconds.
- Do not retry missing credentials, malformed vectors/responses, validation failures, or other HTTP errors.
- Preserve request counts, usage from every attempt, cache ordering, vector validation, provider-detail redaction, and the `EmbeddingError` interface.
- Add no dependency, CLI flag, automatic `.env` loading, result-schema change, or alternate evaluation path.
- User-facing evaluation remains `ghl-mas-evaluate`; tests never sleep or call Gemini.

## Review Focus

- A 429 response with reported usage must count that usage before retrying; covered by the retry-success and exhausted-retry tests.
- A successful retry must not duplicate, reorder, or poison cached vectors; covered by the 21-input batching/cache regression.
- HTTP 400/401/403/404/500 must fail after one request without sleeping; covered by the non-429 parameterized regression.
- Invalid successful wire responses must remain non-retryable; covered by the existing invalid-wire tests plus a no-sleep assertion.
- Four consecutive 429 responses must stop after delays 15/30/60 and expose only sanitized error text; covered by the exhausted-retry regression.

---

### Task 1: Add Bounded 429 Fallback to Gemini Embeddings

**Files:**
- Modify: `evaluation/embeddings.py:17-20,199-245`
- Modify: `tests/test_evaluation.py:188-324`
- Modify: `README.md:107-180`

**Interfaces:**
- Consumes: `GeminiEmbedder.embed(texts: list[str]) -> EmbeddingBatch`, transport exceptions exposing HTTP `code`, `_capture_response`, `sum_usage`, and the existing cache.
- Produces: `_MAX_BATCH_SIZE = 20`, `_RATE_LIMIT_DELAYS = (15, 30, 60)`, and unchanged public embedding/CLI interfaces with bounded 429 fallback.

- [ ] **Step 1: Write failing batching and retry tests**

In `tests/test_evaluation.py`, update the multi-batch expectation to chunks no larger than 20 and add tests with mocked `sleep` asserting:

- 21 inputs produce request sizes `20, 1` and preserve vector order/cache behavior;
- `429 -> success` sends the same batch twice, sleeps `[15]`, includes both attempts in usage/request count, then continues;
- four 429 responses sleep `[15, 30, 60]`, raise sanitized `EmbeddingError`, and report four attempts plus summed usage;
- representative non-429 HTTP statuses make one request and never sleep;
- invalid wire values never sleep.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `UV_CACHE_DIR=/tmp/ghl-mas-uv-cache uv run --extra test pytest tests/test_evaluation.py -q`

Expected: FAIL because batches are still 100 and HTTP 429 fails immediately without sleeping.

- [ ] **Step 3: Implement the minimal fallback**

In `evaluation/embeddings.py`, set the constants from the spec and add a per-batch attempt loop. For each attempt, establish/reset `_CAPTURED_USAGE`, increment request count, append captured usage, and either validate the successful response or handle the exception. Retry only when `getattr(error, "code", None) == 429` and a delay remains; call `sleep(delay)` before repeating the identical batch. Preserve the current sanitized message and raise after the last delay or any non-429 error.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `UV_CACHE_DIR=/tmp/ghl-mas-uv-cache uv run --extra test pytest tests/test_evaluation.py -q`

Expected: PASS with no real delays or network calls.

- [ ] **Step 5: Update README**

Document under automatic evaluation that `ghl-mas-evaluate` sends at most 20 texts per embedding request and automatically retries only 429 responses after 15/30/60 seconds; after exhaustion the run remains partial and the same command can be repeated.

- [ ] **Step 6: Run the full suite**

Run: `UV_CACHE_DIR=/tmp/ghl-mas-uv-cache uv run --extra test pytest -q`

Expected: PASS, with only existing conditional local-data skips.

- [ ] **Step 7: Run the real failed unit through the CLI**

Load the already authorized key from `.env` without printing it, then run:

```bash
ghl-mas-evaluate \
  --run 2026-11-09_09-19-36 \
  --solution GHL \
  --unit firefox_bookmarks
```

Expected: `Evaluation: 1 succeeded, 0 failed; run completed.` If provider quota remains exhausted after the bounded fallback, preserve and report the sanitized failure instead of bypassing the CLI.

- [ ] **Step 8: Commit**

```bash
git add evaluation/embeddings.py tests/test_evaluation.py README.md \
  docs/superpowers/specs/2026-11-09-embedding-rate-limit-fallback-design.md \
  docs/superpowers/plans/2026-11-09-embedding-rate-limit-fallback.md
git commit -m "fix: retry rate-limited embeddings"
```
