# Experiment configuration

```json
{
  "model": "openai/gpt-oss-120b",
  "solutions": [
    "one-shot",
    "GHL",
    "Multiagent"
  ],
  "units": [
    "firefox_bookmarks",
    "e2edev_bench_01"
  ],
  "agents": [
    "analyst",
    "coverage",
    "critic",
    "validator"
  ],
  "output_modes": {
    "one-shot": "batch",
    "GHL": "batch",
    "Multiagent": "batch"
  },
  "max_rounds": 2,
  "generation_retries": 3,
  "timezone": "America/Recife",
  "credential": ".env:GROQ_API_KEY",
  "status": "interrupted",
  "outcomes": {
    "one-shot": {
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 36,
        "usage": {
          "input_tokens": 1089,
          "output_tokens": 2310,
          "details": {
            "reasoning_tokens": 464,
            "total_tokens": 3399
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 10,
        "usage": {
          "input_tokens": 774,
          "output_tokens": 1774,
          "details": {
            "reasoning_tokens": 1057,
            "total_tokens": 2548
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      }
    },
    "GHL": {
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 101,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "state_transition",
          "decision_table",
          "combinatorial",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partitions valid vs invalid bookmark URLs, folder names, keywords and UI inputs address normal and abnormal behavior as required.",
          "boundary_value_analysis": "Tests stated limits such as maximum bookmark title length, maximum number of items in a folder, column width minima/maxima, and edge cases for numeric fields.",
          "state_transition": "Covers states (added, deleted, edited, saved, crash‑recovered) and transitions triggered by user actions, matching the need for state/transition coverage.",
          "decision_table": "Maps combinations of conditions (item type, operation, selection mode) to expected outcomes, fulfilling the condition‑combination requirement.",
          "combinatorial": "Generates meaningful combos of factors (bookmark/folder/separator × add/delete/rename × single/multi‑select) to ensure broad coverage of requirement interactions.",
          "use_case": "Defines end‑to‑end user flows (e.g., add → launch, multi‑delete, drag‑and‑drop reordering) that exercise the complete functional sequences described.",
          "error_guessing": "Explores plausible failures such as invalid URLs, dropping an item onto itself, crashes during save, and other misuse scenarios."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 56,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "state_transition",
          "decision_table",
          "combinatorial",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partitions the product items into valid (properly marked draggable, with title and price) and invalid (missing attributes, non‑draggable) groups to verify normal and abnormal drag behaviour.",
          "boundary_value_analysis": "Tests price and total calculations at limits such as zero price, minimum non‑zero price, maximum reasonable price, and rounding boundaries to ensure correct two‑decimal formatting.",
          "state_transition": "Models the UI states (idle → dragging → dropped → cart‑updated) and verifies allowed and forbidden transitions, covering the drag‑and‑drop lifecycle and cart state changes.",
          "decision_table": "Defines conditions (first‑time product, repeated product, different products) and expected actions (update title, price, quantity) to ensure all combinations are exercised.",
          "combinatorial": "Creates test sets that combine multiple factors (number of items, repeated vs unique, price ranges) to expose interaction faults beyond simple pairwise cases.",
          "use_case": "Executes the end‑to‑end user flow: drag a product, drop into the cart, view updated boxes, and verify the total price, satisfying the overall workflow requirement.",
          "error_guessing": "Explores plausible failure scenarios such as dragging non‑product elements, dropping outside the target area, or corrupting data‑attributes to assess robustness."
        },
        "error_type": null,
        "error_stage": null
      }
    },
    "Multiagent": {
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 10,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_01": {
        "status": "interrupted",
        "case_count": 7,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": "CancelledError",
        "error_stage": null
      }
    }
  }
}
```
