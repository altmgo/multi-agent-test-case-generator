# Critic explicit scenario coverage fix

## Goal
Fix Problem 2: the Critic did not verify missing explicit scenario variants and therefore could not request revisions for incomplete coverage.

## What changed
- The shared review rubric now requires a requirement-by-requirement comparison.
- It distinguishes missing explicit scenarios from blockers and requires `request_revision=true` for actionable coverage gaps.
- Simple declaration/menu-presence requirements are limited to one normal case unless the requirement explicitly describes more behaviors.
- The Critic prompt now requires an explicit scenario inventory and matching case names; generic “fully covered” statements are not sufficient.
- Candidate selection now rewards additional valid distinct cases, while keeping blockers and duplicates in the objective.

## Result
The experiment used only `Multiagent`, all four optional agents, `per_requirement`, and exactly the eight required units:
- coverage: 1.0
- generated_count: 114
- reference_count: 104
- match_count: 96
- precision: 0.8421
- recall: 0.9231
- F1: 0.8807

The Critic fix is present in the code and the trace was generated. However, the initial Critic opinions in all eight units returned `request_revision=false`, with no revision rounds created, so this run did not demonstrate a behavioral improvement from additional revision cycles. Compared with the strongest previous atomic-coverage run (0.9065 precision, 0.9327 recall, 0.9194 F1), this run had lower metrics. The result is retained for reproducibility, and the next iteration should be considered only if it produces actual coverage-gap revisions without degrading precision.
