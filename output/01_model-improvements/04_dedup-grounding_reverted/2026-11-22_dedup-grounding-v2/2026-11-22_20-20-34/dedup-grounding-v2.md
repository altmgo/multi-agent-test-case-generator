# Deduplication and grounding experiment

## Goal
Reduce unmatched extra cases while preserving the recall improvement from the atomic-coverage prompt.

## What changed
I kept the same eight units, Multiagent-only solution, all four optional agents, and `per_requirement` mode. I added stricter merge/deduplication instructions to the generator and critic, asking them to remove setup-only variants and duplicate trigger/expected-outcome pairs.

## Result
The evaluation produced 114 generated cases, 98 matches, and 104 reference cases:
- coverage: 1.0
- precision: 0.8596
- recall: 0.9423
- F1: 0.8991

This variant improved recall by 0.0096 over the first prompt experiment but generated 7 additional unmatched cases and reduced F1 by 0.0203. Because it was worse overall, the merge/deduplication additions were reverted. The retained implementation is the atomic-coverage prompt from `atomic-coverage-v1`.
