# Zero-shot implementation

## Purpose

The zero-shot solution generates high-level test cases in a single model call.
It is the simplest comparison method: it receives the complete set of
requirements for one unit and returns one batch of cases. It has no technique
catalogue, agent roles, candidate rounds, or revision logic.

## Where the implementation lives

- Entry point: [`src/zero_shot/__init__.py`](../../src/zero_shot/__init__.py)
- Shared input and output types: [`src/tcg/schemas.py`](../../src/tcg/schemas.py)
- Model/runtime boundary: [`src/tcg/runtime.py`](../../src/tcg/runtime.py)
- CLI dispatch: [`src/tcg/cli.py`](../../src/tcg/cli.py)

## Code flow

1. The CLI prepares a `GenerationInput` containing the unit ID and all
   requirements.
2. `generate_zero_shot()` records the current position in the runtime usage
   history.
3. It calls `runtime.run()` once with the stage name `zero_shot`.
4. The runtime adds the requirements to the model prompt and constrains the
   answer to the `_CaseBatch` Pydantic model. `_CaseBatch` contains a list of
   `GeneratedCase` objects.
5. `validate_cases()` verifies that every generated case links only to supplied
   requirement IDs.
6. The cases receive stable IDs `G-001`, `G-002`, and so on.
7. The result includes the cases, summed token usage, and prompt version
   `zero-shot-v1`.

Zero-shot always uses batch mode, even if the CLI's `--output-mode` option is
set to another value. This behavior is fixed in `src/tcg/cli.py`.

## Prompt

The instruction sent to the model is:

```text
Generate high-level test cases from all requirements. Include normal and abnormal cases.
Each case must cite only supplied requirement IDs.
```

### What the prompt does

- **"from all requirements"** tells the model to consider the complete unit,
  rather than one selected requirement.
- **"Include normal and abnormal cases"** requests both successful behavior
  and failure or alternative behavior.
- **"cite only supplied requirement IDs"** gives the model a traceability
  requirement.

The prompt is intentionally short. It does not prescribe a test-generation
technique or identify atomic behaviors, so the model decides how to interpret
the requirements and how many cases to produce.

## Validation and failure behavior

The model answer must fit the Pydantic schema before Python receives it. After
the answer arrives, `validate_cases()` performs an additional grounding check:
if a case cites an unknown requirement ID, generation raises `ValueError`.

Usage is measured only for this one call. Provider retries, when needed, are
handled by `Runtime` and remain included in the returned usage data.

## Role in the study

Zero-shot is the no-agent baseline. It is useful for showing what a direct
generation call can do, but it does not have a separate analysis stage, a
review stage, or a mechanism that forces an unacceptable candidate to be
replaced.
