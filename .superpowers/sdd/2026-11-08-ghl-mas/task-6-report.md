# Task 6 report: One-shot and GHL

## Design and paper basis

The catalogue is versioned as `ghl-techniques-v1` and contains equivalence partitioning, boundary value analysis, state transition, decision table, and combinatorial testing. These correspond to the specification-based techniques named in Section II-C of Masuda et al. (2025), which also describes experience-based error guessing. The study adds use-case/user-flow coverage and error guessing as documented adaptations: they are included to support user-facing requirements and requirement-grounded failure exploration. The LLM selector receives every requirement and the full compact catalogue, plus a fixed strategy prompt covering normal/abnormal behavior, input partitions, limits, states, combinations, workflows, and plausible failures. Its output records an individual rationale per selected technique.

This follows Section III's two-step flow: select suitable techniques from the requirements and test strategy, then make one generation call per selected technique. Each generation request carries the full `GenerationInput`; the technique identifier and `output_mode` are included in Runtime `extra`. The paper's test strategy comes from its supplied documents, while this implementation fixes strategy in the prompt because `GenerationInput` has no strategy field. One-shot is one batch call. GHL defaults to one batch per technique and can optionally use `per_technique` output instructions while keeping full requirements in the request.

Reference: [Masuda et al., “Generating High-Level Test Cases from Requirements using LLM: An Industry Study,” Sections II-C and III](https://arxiv.org/html/2510.03641v1#S3).

## Contracts and artifacts

- `generate_one_shot(input, runtime)` performs one call and returns stable `G-001` IDs, validated links, usage, and `prompt_version="one-shot-v1"`.
- `generate_ghl(input, runtime, *, output_mode="batch")` selects techniques once, then calls once per selected technique. It records ordered `selected_techniques`, their `technique_rationales`, and `prompt_version="ghl-v1"` in `GenerationResult`.
- GHL deduplicates only exact `(title, description)` pairs. It unions their requirement links in encounter order and assigns stable IDs after consolidation. It rejects unknown/duplicate technique selections and unknown requirement IDs.
- Runtime supports `output_mode="per_technique"`; this only scopes the requested output and leaves the complete requirement payload unchanged. `batch` remains the default.
- CLI contract: expose optional `--ghl-output-mode {batch,per_technique}` with default `batch`; pass it as the keyword to `generate_ghl`. Keep the selection stage in batch mode. Persist `GenerationResult` so selected technique IDs, rationales, prompt version, and aggregate usage remain auditable. One-shot does not consume this option.

## TDD evidence

- RED: `.venv/bin/python -m pytest tests/test_solutions.py -v` failed at collection with `ModuleNotFoundError: solutions.ghl`, before the implementation modules existed.
- GREEN: `.venv/bin/python -m pytest tests/test_solutions.py -v` passed (4 tests).
- Runtime scope regression: `.venv/bin/python -m pytest tests/test_model_runtime.py tests/test_solutions.py -v` passed (36 tests), including full requirement payload with `per_technique`.
- Full suite: `.venv/bin/python -m pytest` passed (89 tests).
- `git diff --check` passed.

## Files

- Added `solutions/one_shot.py`, `solutions/ghl.py`, and `solutions/__init__.py`.
- Added `tests/test_solutions.py`; extended `tests/test_model_runtime.py` for the scoped mode.
- Extended `schemas.py` with auditable solution metadata and `model_runtime.py` with the `per_technique` mode.

## Caveats

The selector sees a fixed strategy embedded in its prompt; there is no caller-supplied strategy model yet. The adapted use-case and error-guessing entries are explicit catalogue additions, not claims that Section III used those techniques. Exact duplicate matching is case- and whitespace-sensitive by design. No paid API calls were made.
