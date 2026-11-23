# Atomic coverage prompt improvement

## Goal
Improve recall and F1 while retaining 1.0 unit coverage. The baseline generated 86 cases with 82 matches, precision 0.9535, recall 0.7885, and F1 0.8632.

## What changed
I kept all four optional Multiagent agents, the `per_requirement` output mode, the Gemini model, and exactly the eight required units. I only strengthened the analyst and generator prompts:
- the analyst now enumerates explicitly named atomic actions, state transitions, persistence operations, visibility changes, and error conditions;
- the generator now maps each explicit atomic behavior to a distinct focused case and covers explicitly stated restored/empty states.

## Result
The evaluation produced 107 generated cases, 97 matches, and 104 reference cases:
- coverage: 1.0
- precision: 0.9065
- recall: 0.9327
- F1: 0.9194

The run substantially improved recall and F1 over the baseline, but 10 extra or unmatched cases reduced precision. The next experiment will keep the atomic coverage while tightening duplicate and speculative-case reduction.
