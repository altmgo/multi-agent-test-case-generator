# Experiment configuration

```json
{
  "model": "gemini-3.5-flash-lite",
  "solutions": [
    "Multiagent"
  ],
  "units": [
    "firefox_bookmarks",
    "firefox_browser_history",
    "firefox_password_manager",
    "firefox_themes",
    "e2edev_bench_01",
    "e2edev_bench_02",
    "e2edev_bench_03",
    "e2edev_bench_04"
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
  "status": "partial",
  "outcomes": {
    "Multiagent": {
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
        "error_type": "NameError",
        "error_stage": null
      },
      "firefox_browser_history": {
        "status": "generated",
        "case_count": 12,
        "usage": {
          "input_tokens": 7338,
          "output_tokens": 1406,
          "details": {
            "text_prompt_tokens": 7338,
            "total_tokens": 8744
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
      },
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
        "status": "failed",
        "case_count": 0,
        "usage": {
          "input_tokens": 3325,
          "output_tokens": 1385,
          "details": {
            "text_prompt_tokens": 3325,
            "total_tokens": 4710
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": "InvalidCaseSet",
        "error_stage": "generator"
      },
      "e2edev_bench_04": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 9589,
          "output_tokens": 1005,
          "details": {
            "text_prompt_tokens": 9589,
            "total_tokens": 10594
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
