# Multiagent ablation: critic omitted

## Configuration
- Solution: `Multiagent`
- Omitted agent: `critic`
- Enabled agents: `analyst`, `validator`, `coverage`
- Model: `gemini-3.5-flash-lite`
- Output mode: `per_requirement`
- Units: `e2edev_bench_01`, `e2edev_bench_02`, `e2edev_bench_03`, `e2edev_bench_04`, `firefox_bookmarks`, `firefox_browser_history`, `firefox_password_manager`, `firefox_themes`

## Goal
Measure whether the Critic's scenario-risk review and revision control materially improve generation quality. This ablation also checks whether removing the Critic leaves the revision loop with no `critic` checkpoint.

## What was tested
The run kept the Analyst, Validator, and Coverage stages enabled. The Critic was excluded from optional agents, so it could not initiate or continue Critic-driven revision rounds.

## Results
- Unit coverage: `1.0`
- Generated cases: `114`
- Reference cases: `104`
- Matched cases: `93`
- Precision: `0.8157894736842105`
- Recall: `0.8942307692307693`
- F1: `0.8532110091743119`
- Revision rounds across traces: `0`

## Impact analysis
Compared with v4's complete-agent run, removing the Critic reduced precision by 0.0364, recall by 0.0481, and F1 by 0.0418. It also generated 1 fewer case and matched 5 fewer references. The result is consistent with the Critic acting as an important quality-and-revision control.

The trace evidence is especially direct: all eight units had zero revision rounds when the Critic was omitted. This configuration cannot exercise the deterministic Critic fallback or the model Critic blocker/revision checkpoint. The low precision and recall together indicate that its absence affects both overgeneration and missed coverage, rather than being a neutral agent.
