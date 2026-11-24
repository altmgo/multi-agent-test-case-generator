# Model-improvement experiments

This directory records the sequence of implementation hypotheses tested from
20 to 22 November. A directory name states the experimental decision; each
nested run retains its original timestamp, artifacts, `configs.md`, and report.

| Stage | Experiment | Decision | Main evidence |
| --- | --- | --- | --- |
| 01 | Recall expansion | Superseded | Recall reached 0.9135, but speculative cases reduced precision to 0.5367. |
| 02 | Precision calibration | Retained | Precision recovered to 0.9535; this became the basis for subsequent coverage work. |
| 03 | Atomic coverage | Retained | Recall improved to 0.9327 and F1 to 0.9194. |
| 04 | Deduplication and grounding | Reverted | Recall rose slightly, but precision and F1 fell. |
| 05 | Critic explicit coverage | Not validated | The intended revision behavior did not occur and metrics declined. |
| 06 | Deterministic revisions | Reference | Revision fallback became actionable; this is the complete-agent reference for ablations. |

## Reading the folders

- `*_retained`: change retained in the working model at that point.
- `*_superseded`: useful earlier step that was replaced by a later calibration.
- `*_reverted`: experiment kept only for reproducibility; its change was not retained.
- `*_not-validated`: implementation may remain in the code, but the run did not demonstrate the intended benefit.
- `*_reference`: the complete-agent run used as the comparison point for ablation studies.

The agent-removal experiments are stored separately in `../ablation/`.

For the full chronology, including hypotheses, metric changes, decisions, and
the distinction between the best F1 run and the ablation reference, read
[CHRONOLOGY.md](CHRONOLOGY.md).

## Method implementation guides

- [Zero-shot implementation](../03_method-implementations/zero-shot.md)
- [GHL implementation](../03_method-implementations/ghl.md)
- [Multiagent implementation](../03_method-implementations/multiagent.md)
