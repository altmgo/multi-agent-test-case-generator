# Experiment configuration

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
    "firefox_themes",
    "firefox_password_manager",
    "firefox_browser_history"
  ],
  "agents": [
    "analyst",
    "coverage",
    "critic",
    "validator"
  ],
  "output_modes": {
    "Multiagent": "batch"
  },
  "max_rounds": 2,
  "generation_retries": 3,
  "max_retry_wait_seconds": 60,
  "groq_tokens_per_minute": null,
  "reasoning_effort": null,
  "timezone": "America/Recife",
  "credential": ".env:GOOGLE_API_KEY",
  "status": "interrupted",
  "outcomes": {
    "Multiagent": {
      "e2edev_bench_01": {
        "status": "failed",
        "case_count": 0,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": "NameError",
        "error_stage": null
      },
      "e2edev_bench_02": {
        "status": "failed",
        "case_count": 0,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": "NameError",
        "error_stage": null
      },
      "e2edev_bench_03": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": 8867,
          "output_tokens": 1136,
          "details": {
            "text_prompt_tokens": 8867,
            "total_tokens": 10003
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_04": {
        "status": "interrupted",
        "case_count": 12,
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
