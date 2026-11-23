# Experiment configuration

## Consolidated source runs

- `2026-11-23_09-39-03`: source run.
- `2026-11-23_09-53-47`: source run.
- `2026-11-23_09-58-41`: source run.

```json
{
  "model": "gemini-3.5-flash-lite",
  "solutions": [
    "Multiagent"
  ],
  "units": [
    "e2edev_bench_01",
    "e2edev_bench_02",
    "e2edev_bench_03",
    "e2edev_bench_04",
    "firefox_bookmarks",
    "firefox_browser_history",
    "firefox_password_manager",
    "firefox_themes"
  ],
  "agents": [
    "analyst",
    "coverage",
    "critic"
  ],
  "output_modes": {
    "Multiagent": "per_requirement"
  },
  "max_rounds": 2,
  "generation_retries": 3,
  "max_retry_wait_seconds": 60,
  "groq_tokens_per_minute": null,
  "reasoning_effort": null,
  "timezone": "America/Recife",
  "credential": ".env:GOOGLE_API_KEY",
  "status": "completed",
  "outcomes": {
    "Multiagent": {
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 4,
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
      "e2edev_bench_02": {
        "status": "generated",
        "case_count": 12,
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
      "e2edev_bench_03": {
        "status": "generated",
        "case_count": 22,
        "usage": {
          "input_tokens": 18180,
          "output_tokens": 2965,
          "details": {
            "text_prompt_tokens": 18180,
            "total_tokens": 21145
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_04": {
        "status": "generated",
        "case_count": 17,
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
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 26,
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
      "firefox_browser_history": {
        "status": "generated",
        "case_count": 12,
        "usage": {
          "input_tokens": 20919,
          "output_tokens": 1662,
          "details": {
            "text_prompt_tokens": 20919,
            "total_tokens": 22581
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_password_manager": {
        "status": "generated",
        "case_count": 7,
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
      "firefox_themes": {
        "status": "generated",
        "case_count": 7,
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
      }
    }
  }
}
```
