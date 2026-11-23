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
  "status": "partial",
  "outcomes": {
    "Multiagent": {
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 5,
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
        "error_type": "ModelUnavailableError",
        "error_stage": "analyst"
      },
      "e2edev_bench_03": {
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
        "error_type": "ModelUnavailableError",
        "error_stage": "analyst"
      },
      "e2edev_bench_04": {
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
        "error_type": "ModelUnavailableError",
        "error_stage": "generator"
      },
      "firefox_bookmarks": {
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
        "error_type": "ModelUnavailableError",
        "error_stage": "analyst"
      },
      "firefox_browser_history": {
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
        "error_type": "ModelUnavailableError",
        "error_stage": "analyst"
      },
      "firefox_password_manager": {
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
        "error_type": "ModelUnavailableError",
        "error_stage": "analyst"
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
