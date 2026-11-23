# Multiagent ablation: analyst omitted

## Configuration
- Solution: `Multiagent`
- Omitted agent: `analyst`
- Enabled agents: `critic`, `validator`, `coverage`
- Model: `gemini-3.5-flash-lite`
- Output mode: `per_requirement`
- Units: `e2edev_bench_01`, `e2edev_bench_02`, `e2edev_bench_03`, `e2edev_bench_04`, `firefox_bookmarks`, `firefox_browser_history`, `firefox_password_manager`, `firefox_themes`

## Goal
Measure the effect of removing the Analyst from an otherwise unchanged Multiagent run. The Analyst normally produces an explicit requirement-behavior inventory before generation, so this test asks whether its omission materially reduces recall or increases extra cases.

## What was tested
The generation used the deterministic Critic fallback and the same revision budget and selection logic as the complete-agent implementation. Only the Analyst stage was disabled; generation, Critic, Validator, and Coverage remained enabled.

## Results
- Unit coverage: `1.0`
- Generated cases: `95`
- Reference cases: `104`
- Matched cases: `87`
- Precision: `0.9157894736842105`
- Recall: `0.8365384615384616`
- F1: `0.8743718592964824`

## Impact analysis
Removing the Analyst preserved high precision, but recall fell by 0.1058 relative to the v4 complete-agent comparison run (v4 recall `0.9423`) and F1 fell by 0.0206 (v4 F1 `0.8950`). It also generated 20 fewer cases than v4, suggesting that the Analyst primarily adds coverage breadth rather than speculative precision loss.

This result indicates the Analyst was materially useful for recall. It appears to help the generator identify distinct explicit behaviors, particularly across the E2E benchmark units. The result should be treated as one stochastic Gemini run, but the precision/recall split strongly suggests that the Analyst contributed more coverage than it contributed extra cases.
