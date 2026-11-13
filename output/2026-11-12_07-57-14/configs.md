# Experiment configuration

```json
{
  "model": "gemini-3.5-flash-lite",
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
  "max_retry_wait_seconds": 60,
  "groq_tokens_per_minute": null,
  "reasoning_effort": null,
  "timezone": "America/Recife",
  "credential": "v2/.env:GOOGLE_API_KEY",
  "status": "completed",
  "outcomes": {
    "one-shot": {
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 18,
        "usage": {
          "input_tokens": 1024,
          "output_tokens": 1296,
          "details": {
            "text_prompt_tokens": 1024,
            "total_tokens": 2320
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
        "case_count": 4,
        "usage": {
          "input_tokens": 641,
          "output_tokens": 360,
          "details": {
            "text_prompt_tokens": 641,
            "total_tokens": 1001
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
        "case_count": 60,
        "usage": {
          "input_tokens": 5540,
          "output_tokens": 4764,
          "details": {
            "text_prompt_tokens": 5540,
            "total_tokens": 10304
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partitioning valid and invalid input classes such as valid hierarchy locations, valid links in packaged default files, and valid/invalid property views.",
          "state_transition": "Covering the life cycle states of bookmarks, folders, and separators including addition, modification, renaming inline, and deletion.",
          "use_case": "Covering end-to-end user flows for managing bookmarks, folders, and toolbars such as searching by keyword, sorting columns, and launching items.",
          "error_guessing": "Exploring plausible failure conditions and negative behaviors such as dropping a bookmark onto itself or its immediate parent/child, abnormal restart/crash persistence, and negative view properties."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 11,
        "usage": {
          "input_tokens": 3625,
          "output_tokens": 1206,
          "details": {
            "text_prompt_tokens": 3625,
            "total_tokens": 4831
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover important input partitions such as different and repeated products dropped into the cart.",
          "state_transition": "Cover the states and transitions of product items being dragged, dropped, and updating the cart display and total price.",
          "use_case": "Cover end-to-end user flows including dragging products from the list, dropping them into the designated drop area, and verifying cart updates and total price calculation.",
          "error_guessing": "Explore plausible failures such as dropping invalid elements or handling formatting of the total price with the currency symbol."
        },
        "error_type": null,
        "error_stage": null
      }
    },
    "Multiagent": {
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 18,
        "usage": {
          "input_tokens": 9219,
          "output_tokens": 2345,
          "details": {
            "text_prompt_tokens": 9219,
            "total_tokens": 11564
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
        "case_count": 3,
        "usage": {
          "input_tokens": 4505,
          "output_tokens": 871,
          "details": {
            "text_prompt_tokens": 4505,
            "total_tokens": 5376
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      }
    }
  }
}
```
