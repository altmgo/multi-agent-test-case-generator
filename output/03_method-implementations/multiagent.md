# Multiagent implementation

## Purpose

Multiagent is the most structured solution in this repository. It creates an
initial candidate, can divide work among specialized agents, validates and
critiques candidates, generates replacement candidates when requested, scores
and compares them, and performs a final coverage review.

The implementation is bounded: the CLI sets `MAX_ROUNDS = 2`, and each revision
round creates three candidates. Optional agents are configurable, but the
orchestrator always preserves the shared candidate and trace data.

For the Multiagent experiment chronology and metric decisions, read:

- [`CHRONOLOGY.md`](../01_model-improvements/CHRONOLOGY.md)
- [`Model-improvement experiments`](../01_model-improvements/README.md)
- [`Ablation experiments`](../02_ablation/README.md)

## Where the implementation lives

- Orchestrator: [`src/multiagent/orchestrator.py`](../../src/multiagent/orchestrator.py)
- Analyst: [`src/multiagent/analyst.py`](../../src/multiagent/analyst.py)
- Generator: [`src/multiagent/generator.py`](../../src/multiagent/generator.py)
- Critic: [`src/multiagent/critic.py`](../../src/multiagent/critic.py)
- Validator: [`src/multiagent/validator.py`](../../src/multiagent/validator.py)
- Coverage: [`src/multiagent/coverage.py`](../../src/multiagent/coverage.py)
- Candidate scoring and selection: [`src/multiagent/selection.py`](../../src/multiagent/selection.py)
- State and audit trace: [`src/multiagent/state.py`](../../src/multiagent/state.py)

## Chronological evolution of the prompts and control logic

The current implementation is the final reference behavior, `multiagent-v3`,
not a snapshot of every earlier experiment.

- **Stage 01 — Recall expansion:** prompts began enumerating Normal, Edge,
  Boundary, and Abnormal/Error scenarios and asked the Generator to create
  distinct supported types. This solved undergeneration but greatly increased
  overgeneration, so it was superseded.
- **Stage 02 — Precision calibration:** Analyst and Generator prompts were
  grounded in explicit requirement text. A simple declarative requirement
  was to receive one normal case. This recovered precision and became the
  foundation for later work.
- **Stage 03 — Atomic coverage:** the prompts began enumerating each explicit
  action, transition, persistence operation, visibility change, and error
  condition. This is the best-F1 configuration observed: 97 of 104 references
  matched, with F1 0.9194.
- **Stage 04 — Deduplication and grounding:** merge and deduplication guidance
  was added to Generator and Critic. It produced slightly higher recall but
  lower precision and F1, and was reverted.
- **Stage 05 — Critic explicit coverage:** the Critic was asked to match every
  explicitly described behavior to a case and trigger revision. It did not
  demonstrate revision behavior reliably, so it was not validated.
- **Stage 06 — Deterministic revisions:** the orchestrator stopped relying only
  on the model's Critic opinion for explicit scenario pairs. It deterministically
  checks paired terms and missing requirement links, then replaces the Critic
  opinion with an actionable revision request. This mechanism is the
  complete-agent reference for ablations.

The current code combines Stage 02's grounding, Stage 03's atomic-behavior
focus, and Stage 06's deterministic revision fallback. The Stage 04 merge
guidance is not present as a strict automatic merge in the final implementation.

## Shared input and output contracts

Before generation, `tcg.cli` creates a `GenerationInput` for one unit:

- `unit_id`;
- the unit's requirements;
- each requirement's ID and text.

Every generated case must contain:

- an ID;
- a title;
- a description;
- at least one supplied requirement ID.

`validate_cases()` rejects cases that link to unknown requirement IDs. Generator
output is also checked for the targeted requirement in `per_requirement` and
`per_case` modes.

## The overall flow

The orchestrator is `run_multiagent()` in `src/multiagent/orchestrator.py`.
The flow is:

1. Create the initial `CandidateAssessment`, with ID `initial` and an empty case
   list.
2. Run the Analyst, if enabled, then run the Generator.
3. Accept the initial candidate as the baseline.
4. Run enabled controls in fixed order: Critic, then Validator.
5. If a control requests revision and rounds remain, generate three candidates.
6. Run the same control prefix on every candidate.
7. Compare candidates with the accepted baseline.
8. Keep the baseline unless a candidate is a proven improvement.
9. Continue until the round limit, no improvement, or checkpoint completion.
10. If Coverage is enabled, perform one advisory coverage review of the final
    accepted cases.

The accepted case set is preserved on disk as the final result. The complete
trace is available in `intermediate/trace.json` and includes initial state,
round decisions, candidates, opinions, failures, and coverage feedback.

## Agent 1: Analyst

### Role

The Analyst produces a concise behavioral analysis before generation. It helps
the Generator identify which behaviors are explicit and which uncertainty or
scenarios should not be invented.

### Code

`analyze()` in `src/multiagent/analyst.py` sends an `Analysis` request to the
runtime. The call includes:

- the candidate ID;
- the revision context, if this is a revised candidate;
- the complete requirement set supplied implicitly by `StageRunner`.

For revisions, the Analyst receives accepted state, requester, feedback, and
other revision metadata, but not the accepted cases themselves. Its job is to
explain what needs to change in the next generation attempt.

### Prompt

The Analyst instruction is:

```text
Identify testable behavior, boundaries, normal and abnormal paths, and ambiguities.
Use every requirement. For each requirement, identify whether it describes only a single
straightforward acceptance criterion or multiple distinct behaviors. Only list distinct
scenario types (Edge, Boundary, Abnormal/Error) if the requirement text explicitly mentions
conditions, parameters, or failure paths for them. Never invent hypothetical edge cases,
corrupted states, or negative scenarios not mentioned in the requirement.
Enumerate the explicit atomic behaviors for each requirement: each named action, state
transition, selection, persistence operation, visibility change, or error condition is a
separate behavior to cover. For each atomic behavior, record the exact trigger and expected
outcome stated or directly implied by that requirement. Do not infer behaviors from examples
outside the requirement.
If a requirement is a simple declaration (e.g. menu presence, display existence), specify
that only a single Normal test scenario is warranted.
For revisions, address feedback on the accepted state and mark each scenario type as covered
or missing. Return concise findings grouped by requirement ID. Focus on actionable conditions
and gaps.
```

### Prompt explanation

The Analyst's grounding rules come directly from the precision and atomic-
coverage stages:

- It distinguishes a single declarative requirement from one with multiple
  explicit behaviors.
- Edge, Boundary, and Abnormal/Error scenarios are allowed only when the
  requirement text explicitly supports them.
- Every named action or state transition becomes an atomic behavior.
- Persistence and UI visibility changes are explicitly recognized.
- The trigger and expected outcome must be tied to the requirement.
- In revision mode, the Analyst maps feedback to covered and missing scenarios.

This is the first of the two grounding barriers: the Analyst tells the
Generator what behavior is real.

## Agent 2: Generator

### Role

The Generator creates the proposed case set. It can run once for the initial
candidate or three times in a revision round.

### Code

`generate()` calls the runtime once for each target:

- `batch`: one call with target `None`;
- `per_requirement`: one call per requirement;
- `per_case`: one call per requirement and exactly one case per call.

Every answer is added to the candidate assessment with a fresh stable ID.
The code then performs structural validation. It fails if:

- a case links outside the supplied requirements;
- a scoped case does not link to its target requirement;
- `per_case` returns more than one case;
- the Pydantic/schema contract is violated.

### Prompt

The Generator instruction is:

```text
Generate concise, high-level test cases with clear expected behavior and links only to
supplied IDs.
Ground every test strictly and directly in the explicit requirement text and any analysis.
Do NOT invent speculative, hypothetical, or unstated conditions (such as missing files,
network errors, corrupted assets, window resizing, or boundary placements) unless explicitly
mentioned in the requirement text.
If a requirement is simple (e.g., verifying a menu item, theme existence, or UI element
presence), generate exactly one focused normal case for it.
For requirements with multiple explicitly described atomic behaviors, generate a complete set
that has one distinct, focused case for each named action or state transition (for example,
select and deselect are separate behaviors; add and delete are separate behaviors; edit mode
and view mode are separate behaviors).
For persistence requirements, cover both the normal saved state and the explicitly described
empty or restored state when each is stated.
Only generate additional scenario types (Edge, Boundary, Error) if the requirement text
explicitly defines multiple distinct operations, parameters, ranges, or error conditions.
Avoid redundant or overlapping test cases.
For revisions, use the accepted cases and feedback to generate a complete replacement for
the requested scope, keeping sound coverage.
```

### Prompt explanation

This prompt combines the Stage 02 precision rules and Stage 03 atomic coverage
rules:

- “Ground every test” prevents unsupported expected behavior.
- Exactly one normal case is required for a simple declaration.
- Multiple explicit behaviors produce separate focused cases.
- Saved, empty, and restored states are handled only when the requirement states
  them.
- Additional Edge, Boundary, and Error cases need textual support.
- Revisions replace the scope instead of incrementally appending uncoordinated
  cases.

The Generator is also forbidden to invent concrete speculative examples such
as corrupted files or network failures unless those conditions are written in
the requirement.

## Agent 3: Critic

### Role

The Critic compares the candidate with the requirements and decides whether a
revision is needed. It can report confirmed blockers and explicit scenario gaps.

### Code

`critique()` obtains a `ControlOutput` from the model. That output contains:

- `feedback`;
- `request_revision`;
- `confirmed_blockers`;
- `blocker_assessment_complete`;
- `missing_scenario_gaps`.

If the model supplies `missing_scenario_gaps`, the code forces
`request_revision=true` and appends those gaps to the feedback.

### Prompt

```text
Critique the proposed high-level cases for testability, explicit scenario coverage, distinct
scenarios, and risk. Compare the supplied requirements against the cases before deciding
whether revision is needed.
Do not merely assert that coverage is complete. For every requirement, list its explicitly
described Normal/Edge/Boundary/Abnormal/Error behaviors and name the matching case for each
behavior.
If any explicit behavior has no matching case, set request_revision=true and identify the
exact requirement ID and missing behavior in feedback. Generic impressions of coverage are
insufficient evidence.
```

This is followed by the shared `REVIEW_RUBRIC`.

### Shared review rubric

The rubric used for the Critic and Validator asks the model to:

- report only concise, requirement-grounded blockers;
- mark blocker evidence as complete or inconclusive;
- compare every requirement with proposed cases;
- treat missing explicitly described scenarios as coverage gaps;
- avoid requesting speculative scenarios;
- flag unsupported, redundant, or excessive cases;
- request revision only for confirmed blockers, confirmed excess, or actionable
  explicit gaps.

The shared rubric implements the calibration learned across the first four
model-improvement stages: more coverage is not automatically better; cases
must be grounded and distinct.

### Deterministic fallback

Stage 05 showed that prompt-only Critic instructions did not reliably create
a revision round. Stage 06 therefore added `_explicit_coverage_opinion()` in
the orchestrator.

This fallback has a fixed pair catalogue:

| Paired behaviors |
| --- |
| add / delete |
| create / delete |
| edit / view |
| enable / disable |
| open / close |
| show / hide |
| select / deselect |
| save / delete |
| valid / invalid |
| normal / error |
| empty / restored |
| single / multiple |

For each requirement, the fallback:

1. Finds which paired terms occur in the requirement text.
2. Finds cases linked to that requirement.
3. Searches the candidate titles and descriptions for the paired terms.
4. Creates a gap for each term that is not covered.
5. Creates a gap if the requirement has no linked case.

If gaps exist, the code replaces the Critic opinion with a deterministic
`request_revision=true` opinion. This does not depend on the model choosing
to report a revision. It is the key control mechanism in the current
`multiagent-v3` implementation.

## Agent 4: Validator

### Role

The Validator checks whether cases are executable, grounded, traceable, and
supported by their linked requirements.

It does not make the final selection decision. It supplies an opinion that is
used to count blockers and include or exclude candidate cases.

### Code

`validate()` sends the candidate cases to the runtime and converts the returned
`ControlOutput` into an `AgentOpinion`.

### Prompt

```text
Verify that the cases and expected behavior follow the requirements and their cited IDs.
```

The Validator then receives the shared `REVIEW_RUBRIC`, which establishes that:

- a blocker prevents execution or states unsupported behavior;
- inconclusive evidence should keep blocker completion false;
- explicit missing scenarios are gaps, not blockers;
- speculative and redundant cases should be identified;
- revision is warranted only for confirmed blocker fixes, confirmed excess,
  or actionable coverage gaps.

The Validator's main value is independent traceability and testability review.
Its opinion can block a candidate even when the candidate has many cases.

## Agent 5: Coverage

### Role

Coverage is advisory rather than controlling. It examines the final accepted
candidate and lists missing or excessive coverage, but it does not
automatically create a revision round.

### Code

`review_coverage()` builds a `case_index` containing:

- the accepted candidate's cases;
- each rejected candidate's ID, title, and requirement links.

Rejected cases are context only. The final answer is a `CoverageReport`
containing feedback.

### Prompt

```text
Advise on coverage gaps, excess, overgeneration, and repetition in the accepted cases.
Flag cases that test speculative or unstated behaviors not grounded in the requirement text
as excess.
For each requirement, check whether the accepted cases cover what is explicitly described
in the requirement without generating redundant or fabricated edge/error cases.
List missing requirements or explicit scenario types as gaps.
Use rejected cases as context only.
Compare coverage against the supplied requirements.
Return feedback only.
```

### Prompt explanation

Coverage adds a final independent view of both undergeneration and
overgeneration:

- It separates excess, repetition, and missing coverage.
- It rejects fabricated edge/error scenarios.
- It compares explicit behavior with the final accepted set.
- It does not use rejected cases as decisions, only as context.

Coverage is placed after the revision loop, so it summarizes the final outcome
instead of controlling one more round.

## Candidate scoring

After each candidate receives controls, `score_assessment()` in
`src/multiagent/selection.py` updates:

- `confirmed_blockers`;
- `covered_requirements`;
- `duplicates`;
- `comparable`.

`distinct_cases` is determined by a normalized pair of title and description.
The covered-requirement count is based on the union of requirement IDs linked
to distinct cases.

The candidate ranking, in order of priority, is:

1. fewer confirmed blockers;
2. more valid distinct cases;
3. more covered requirements;
4. fewer duplicate cases.

This ordering means that the orchestrator should not accept a larger candidate
set merely because it contains more cases. It must first reduce confirmed
blockers.

## Candidate selection and revision rounds

When a control requests revision, the orchestrator creates up to three
candidates for `round-1` or `round-2`.

Each candidate:

- receives the same Analyst instruction;
- receives the accepted candidate and feedback as revision context;
- is regenerated;
- receives the controls that have already run;
- receives the deterministic Critic fallback if the requester is Critic.

The selection module then compares candidates with the accepted baseline:

| Comparison | Meaning |
| --- | --- |
| `improves` | Candidate has a proven better score |
| `ties` | Candidate and baseline have equal proven score |
| `worse` | Candidate has a proven worse score |
| `invalid` | Candidate failed validation or generation |
| `incompatible` | Candidate did not receive the same control opinions |
| `unassessed` | Evidence is incomplete |

The orchestrator keeps the accepted candidate unless a strict improvement is
proven. If an improvement is uncertain, it may call the model-based Selection
stage for a qualitative ranking.

## Selection prompt

The Selection stage is used when objective scores leave ambiguity. It receives
the accepted state and eligible candidates and uses this instruction:

```text
Apply the same rubric to the accepted state and every supplied candidate.
Favor fewer confirmed blockers, more valid distinct cases, more requirements covered,
and fewer duplicates, in that order. Only count cases that cover explicitly described
scenarios.
Where counts leave uncertainty, compare case grounding, testability and distinct scenarios.
Classify every candidate relative to accepted.
Name the best strict improvement if supported and explain your choice.
Preserve accepted if evidence supports a tie, a regression, or no clear improvement.
```

The selection answer includes a preferred ID, rationale, and candidate
judgments. The code does not automatically trust model preference: it only
allows proven improvements or unresolved candidate judgments to participate
in the final decision.

## Optional-agent behavior

The CLI's `--agents` argument selects optional stages:

- `analyst`: adds behavioral analysis before each generation;
- `critic`: adds Critic checkpoint review;
- `validator`: adds Validator checkpoint review;
- `coverage`: adds the final advisory coverage report.

Removing an optional agent removes that stage from the run. The complete-agent
reference is Stage 06 with all four agents. It is used for the ablation
studies stored in [`output/02_ablation`](../02_ablation).

## Revision budget and stopping conditions

The orchestrator allows at most two revision rounds. For each round, it creates
three candidates and records why execution stopped:

- `round_limit`: the accepted candidate still has a revision request after both
  rounds;
- `no_improvement`: candidate selection preserved the baseline;
- `checkpoint_passed`: the control did not continue as a revision requester.

The trace also marks monotonicity as `unverified` if the model-based selector
cannot prove that a qualitative improvement is better.

## Output modes

Multiagent supports:

- `batch`: generate the complete set in one call per candidate;
- `per_requirement`: make one generation call for each requirement;
- `per_case`: make one call per requirement and require one generated case.

The CLI documents `per_requirement` and `per_case` as GHL and Multiagent modes.
The benchmark chronology used `per_requirement`, which also makes traceability
and requirement scoping easy to inspect.

## Trace and final result

`RunTrace` stores the initial attempt, revision rounds, candidate decisions,
accepted candidate, pending revisions, Coverage report, and stage calls.
`trace.result()` produces the `GenerationResult` consumed by the CLI.

For each unit, the output writer creates:

- `requirements_to_tests.md`;
- one requirement Markdown file per requirement;
- test-case Markdown files;
- `intermediate/trace.json`;
- initial and round JSON records.

This trace is important for the chronology: it lets the repository distinguish
prompt-only revisions from revisions that the deterministic fallback actually
triggered.
