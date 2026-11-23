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
    "firefox_browser_history",
    "firefox_password_manager",
    "firefox_themes"
  ],
  "agents": [
    "analyst",
    "coverage",
    "critic",
    "validator"
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
        "case_count": 5,
        "usage": {
          "input_tokens": 7930,
          "output_tokens": 1053,
          "details": {
            "text_prompt_tokens": 7930,
            "total_tokens": 8983
          },
          "status": "available"
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
        "case_count": 21,
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
      "e2edev_bench_04": {
        "status": "generated",
        "case_count": 16,
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
        "case_count": 25,
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
      "firefox_password_manager": {
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
      "firefox_themes": {
        "status": "generated",
        "case_count": 8,
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
