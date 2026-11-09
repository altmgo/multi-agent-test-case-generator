# Embedding Rate-Limit Fallback Design

## Intent

Make `ghl-mas-evaluate` complete large evaluations under Gemini embedding rate limits without external scripts or manual batching.

## Goals

- Limit each Gemini embedding request to 20 canonical texts.
- Retry only HTTP `429` failures for the same batch after 15, 30, and 60 seconds.
- Count usage and request attempts across failed retries and successful batches.
- Preserve cache ordering, vector validation, provider-detail redaction, and the existing `EmbeddingError` contract.
- Keep `ghl-mas-evaluate` as the only user-facing evaluation command and document the fallback.

## Non-goals and constraints

- Do not retry authentication, validation, malformed-response, or other HTTP errors.
- Do not load `.env` automatically, add dependencies, add CLI flags, or change result schemas.
- After the final 429 retry fails, persist the existing sanitized evaluation failure so the CLI can be run again.
- Tests replace sleeping and HTTP transport; they must not wait or call Gemini.

## Approaches

1. **Fixed batches and bounded 429 fallback (selected).** Batch 20 inputs and retry 429 responses after 15/30/60 seconds. Predictable provider traffic and a small implementation.
2. **Recursive adaptive splitting.** Rejected because splitting alone does not handle accumulated per-minute quota and adds more state.

## Scope

Change `evaluation/embeddings.py`, its focused tests, and the evaluation section of `README.md`. Verify the full suite, then run the real `ghl-mas-evaluate --run 2026-11-09_09-19-36 --solution GHL --unit firefox_bookmarks` with the already authorized `.env` key.
