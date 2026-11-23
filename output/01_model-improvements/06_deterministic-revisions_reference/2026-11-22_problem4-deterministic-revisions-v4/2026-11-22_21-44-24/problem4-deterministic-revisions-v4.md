# Problem 4 deterministic revision fallback

## Goal
Fix the observation that revision rounds never start because Critic/Coverage model opinions can leave `request_revision=false` or remain non-actionable.

## What changed
- Added a deterministic explicit-scenario comparison to the Multiagent orchestrator.
- The fallback checks every requirement and its linked cases for paired explicit behaviors, including add/delete, create/delete, edit/view, enable/disable, open/close, show/hide, select/deselect, save/delete, valid/invalid, normal/error, empty/restored, and single/multiple.
- It also detects requirements with no linked test case.
- When the fallback finds a gap, the Critic opinion is replaced with an actionable `request_revision=true` opinion before the revision loop starts.
- Each revision candidate is checked again; when the gap remains, the candidate receives the fallback opinion, and when resolved, no fallback revision is retained.
- The prompt version is now `multiagent-v3`.

## Results
- status: completed
- unit coverage: 1.0
- generated_count: 115
- reference_count: 104
- match_count: 98
- precision: 0.8522
- recall: 0.9423
- F1: 0.8950

This run confirms that revision rounds are now technically actionable. `e2edev_bench_03` created one revision round: the deterministic fallback found a missing explicit deselect scenario for `e2edev_bench_03-R-5`, generated three candidates, and selected `round-1-candidate-3`. The other seven units remained at the initial candidate and showed zero revision rounds.
