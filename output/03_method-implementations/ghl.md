# Grounded High-Level (GHL) implementation

## Purpose

GHL, or Grounded High-Level generation, performs a fixed two-phase process:

1. Ask the model to select useful test-design techniques from a fixed catalogue.
2. Generate cases once for each selected technique, using only requirements
   and information supplied by the system.

GHL is more structured than zero-shot, but it does not contain multiple
reviewing agents or a Multiagent revision round.

## Where the implementation lives

- Entry point and catalogue: [`src/ghl/__init__.py`](../../src/ghl/__init__.py)
- Shared output types: [`src/tcg/schemas.py`](../../src/tcg/schemas.py)
- Model/runtime boundary: [`src/tcg/runtime.py`](../../src/tcg/runtime.py)
- CLI dispatch: [`src/tcg/cli.py`](../../src/tcg/cli.py)

## Fixed technique catalogue

The catalogue is versioned as `ghl-techniques-v1`. It contains:

| Technique | Main purpose |
| --- | --- |
| Equivalence partitioning | Partition valid and invalid input or behavior classes |
| Boundary value analysis | Exercise values at, within, and outside stated limits |
| State transition testing | Cover states, events, transitions, and forbidden transitions |
| Decision table testing | Cover condition combinations and resulting actions |
| Combinatorial testing | Cover meaningful combinations of requirement factors |
| Use-case / user-flow testing | Cover an end-to-end workflow described by the requirements |
| Error guessing | Explore plausible grounded misuse and failures |

The entries are fixed Python objects. GHL does not discover new techniques
from the model; the model can only choose identifiers from this catalogue.

## Code flow

### 1. Select techniques

`generate_ghl()` starts by sending the complete requirement set to
`runtime.run()` under the stage name `ghl_select_techniques`.

The answer must be a `_Selection` object: a list of `TechniqueChoice` entries,
where each choice contains a catalogue technique ID and a rationale. The
selector may return an empty list.

The code checks every returned ID against the fixed catalogue and rejects
unknown IDs or duplicate selections.

### 2. Prepare output scope

GHL supports three output modes:

- `batch`: make one generation call for a selected technique.
- `per_requirement`: make one generation call for the technique and for every
  requirement.
- `per_case`: make one call for a technique and requirement, and require that
  the call return exactly one case.

The selected scope is also appended to the runtime prompt for the generation
call.

### 3. Generate cases for each technique

For every selected technique and every applicable scope, GHL calls
`runtime.run()` with a structured `_CaseBatch` output model.

The generation instruction includes:

- the selected technique name;
- the catalogue rationale;
- a request to consider all supplied requirements;
- a request for normal and abnormal cases;
- a restriction to supplied requirement IDs.

Before a result is added to the collection, `validate_cases()` checks all
requirement links. In `per_requirement` and `per_case` modes, GHL additionally
requires the case to link to the current targeted requirement.

### 4. Consolidate duplicate cases

After all technique calls finish, `_result()` consolidates the collected
cases.

The deduplication rule is deliberately simple:

- Only an exact match of `(title, description)` is merged.
- There is no text normalization or fuzzy matching.
- Requirement IDs from duplicates are combined and deduplicated while preserving
  their order.
- Final IDs are reassigned as `G-001`, `G-002`, and so on.

This differs from the later Multiagent design: GHL does not score candidates or
perform an acceptance/revision decision.

## Selection prompt

The exact instruction for choosing techniques is:

```text
Select only useful test design techniques from the supplied catalogue based on all requirements.
Consider this fixed test strategy: cover normal and abnormal behavior, important input partitions,
stated limits, states and transitions, condition combinations, user flows, and plausible failures.
Return a rationale for every selection; return an empty selection if none apply.
```

### What the selection prompt means

- The model must justify every chosen technique.
- It is not allowed to invent techniques outside the supplied catalogue.
- “Useful” depends on the requirements, not on a requirement to select every
  technique.
- Empty selection is valid and means GHL can produce no cases.
- The fixed strategy describes the broad coverage areas that the catalogue
  represents.

## Generation prompt

For a selected technique, GHL builds this instruction:

```text
Generate high-level test cases using <technique name>. <technique rationale>
Use all requirements supplied in context, include normal and abnormal cases, and cite only supplied IDs.
```

The runtime also adds one of these scope instructions:

```text
Return the requested cases together in a single output.
```

```text
Return cases only for the requirement targeted by this stage.
```

```text
Return only the single case targeted by this stage.
```

### What the generation prompt means

The technique name and rationale tell the model how to frame the cases.
“Use all requirements supplied in context” prevents GHL from narrowing itself
unintentionally when generating in batch mode. The normal/abnormal instruction
allows alternatives, while the ID restriction preserves traceability.

In `per_requirement` mode, the code also enforces that every result belongs to
the target requirement; in `per_case` mode, it rejects answers containing more
than one case.

## Failure and partial-result behavior

GHL has a dedicated `GHLFailure`. If a technique generation call fails, GHL
preserves all cases collected before that failure and records:

- the failed stage;
- the exception type;
- the partial result.

Cancellation is handled separately. A cancelled run attaches its partial
GHL result to the cancellation so the CLI can save already generated cases.

## Relationship to the study

GHL is the baseline for catalogue-guided test design. Compared with
zero-shot, it adds explicit technique selection and optionally separates
generation by requirement or case. It does not yet provide an agent that
compares alternatives against one another or applies a bounded revision loop.
