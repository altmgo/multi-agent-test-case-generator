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
    "e2edev_bench_01",
    "e2edev_bench_02",
    "e2edev_bench_03",
    "e2edev_bench_04",
    "e2edev_bench_05",
    "e2edev_bench_06",
    "e2edev_bench_07",
    "e2edev_bench_08",
    "e2edev_bench_09",
    "e2edev_bench_10",
    "e2edev_bench_11",
    "e2edev_bench_12",
    "e2edev_bench_13",
    "e2edev_bench_15",
    "e2edev_bench_18",
    "e2edev_bench_19",
    "e2edev_bench_20",
    "e2edev_bench_21",
    "e2edev_bench_22",
    "e2edev_bench_24",
    "e2edev_bench_25",
    "e2edev_bench_26",
    "e2edev_bench_27",
    "e2edev_bench_28",
    "e2edev_bench_29",
    "e2edev_bench_30",
    "e2edev_bench_32",
    "e2edev_bench_36",
    "e2edev_bench_37",
    "e2edev_bench_40",
    "e2edev_bench_42",
    "e2edev_bench_44",
    "e2edev_bench_46",
    "e2edev_bench_48",
    "e2edev_bench_49",
    "e2edev_bench_51",
    "e2edev_bench_52",
    "e2edev_bench_57",
    "e2edev_bench_59",
    "e2edev_bench_60",
    "e2edev_bench_601",
    "e2edev_bench_602",
    "e2edev_bench_603",
    "e2edev_bench_63",
    "e2edev_bench_64",
    "e2edev_bench_66",
    "firefox_bookmarks",
    "firefox_browser_history",
    "firefox_clipboard_and_drag_drop",
    "firefox_form_manager",
    "firefox_help",
    "firefox_image_and_embedded_content",
    "firefox_media_plugins",
    "firefox_password_manager",
    "firefox_printing",
    "firefox_search",
    "firefox_sidebar",
    "firefox_text_selection",
    "firefox_themes",
    "firefox_toolbar",
    "firefox_web_location"
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
  "credential": ".env:GOOGLE_API_KEY",
  "status": "partial",
  "outcomes": {
    "one-shot": {
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 4,
        "usage": {
          "input_tokens": 641,
          "output_tokens": 384,
          "details": {
            "text_prompt_tokens": 641,
            "total_tokens": 1025
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
      },
      "e2edev_bench_03": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 1320,
          "output_tokens": 670,
          "details": {
            "text_prompt_tokens": 1320,
            "total_tokens": 1990
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
        "case_count": 6,
        "usage": {
          "input_tokens": 1360,
          "output_tokens": 603,
          "details": {
            "text_prompt_tokens": 1360,
            "total_tokens": 1963
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_05": {
        "status": "generated",
        "case_count": 8,
        "usage": {
          "input_tokens": 1483,
          "output_tokens": 796,
          "details": {
            "text_prompt_tokens": 1483,
            "total_tokens": 2279
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_06": {
        "status": "generated",
        "case_count": 5,
        "usage": {
          "input_tokens": 1142,
          "output_tokens": 485,
          "details": {
            "text_prompt_tokens": 1142,
            "total_tokens": 1627
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_07": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 1052,
          "output_tokens": 542,
          "details": {
            "text_prompt_tokens": 1052,
            "total_tokens": 1594
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_08": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": 1141,
          "output_tokens": 687,
          "details": {
            "text_prompt_tokens": 1141,
            "total_tokens": 1828
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_09": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 976,
          "output_tokens": 538,
          "details": {
            "text_prompt_tokens": 976,
            "total_tokens": 1514
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_10": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": 1175,
          "output_tokens": 680,
          "details": {
            "text_prompt_tokens": 1175,
            "total_tokens": 1855
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_11": {
        "status": "generated",
        "case_count": 10,
        "usage": {
          "input_tokens": 1287,
          "output_tokens": 920,
          "details": {
            "text_prompt_tokens": 1287,
            "total_tokens": 2207
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_12": {
        "status": "generated",
        "case_count": 3,
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
      "e2edev_bench_13": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 1222,
          "output_tokens": 553,
          "details": {
            "text_prompt_tokens": 1222,
            "total_tokens": 1775
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_15": {
        "status": "generated",
        "case_count": 10,
        "usage": {
          "input_tokens": 1307,
          "output_tokens": 1062,
          "details": {
            "text_prompt_tokens": 1307,
            "total_tokens": 2369
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_18": {
        "status": "generated",
        "case_count": 9,
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
      "e2edev_bench_19": {
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
      "e2edev_bench_20": {
        "status": "generated",
        "case_count": 6,
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
      "e2edev_bench_21": {
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
      },
      "e2edev_bench_22": {
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
      "e2edev_bench_24": {
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
      "e2edev_bench_25": {
        "status": "generated",
        "case_count": 5,
        "usage": {
          "input_tokens": 824,
          "output_tokens": 539,
          "details": {
            "text_prompt_tokens": 824,
            "total_tokens": 1363
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_26": {
        "status": "generated",
        "case_count": 8,
        "usage": {
          "input_tokens": 2098,
          "output_tokens": 820,
          "details": {
            "text_prompt_tokens": 2098,
            "total_tokens": 2918
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_27": {
        "status": "generated",
        "case_count": 8,
        "usage": {
          "input_tokens": 1483,
          "output_tokens": 837,
          "details": {
            "text_prompt_tokens": 1483,
            "total_tokens": 2320
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_28": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 1822,
          "output_tokens": 598,
          "details": {
            "text_prompt_tokens": 1822,
            "total_tokens": 2420
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_29": {
        "status": "generated",
        "case_count": 8,
        "usage": {
          "input_tokens": 2035,
          "output_tokens": 1037,
          "details": {
            "text_prompt_tokens": 2035,
            "total_tokens": 3072
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_30": {
        "status": "generated",
        "case_count": 5,
        "usage": {
          "input_tokens": 1859,
          "output_tokens": 665,
          "details": {
            "text_prompt_tokens": 1859,
            "total_tokens": 2524
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_32": {
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
      },
      "e2edev_bench_36": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 985,
          "output_tokens": 586,
          "details": {
            "text_prompt_tokens": 985,
            "total_tokens": 1571
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_37": {
        "status": "generated",
        "case_count": 3,
        "usage": {
          "input_tokens": 1144,
          "output_tokens": 452,
          "details": {
            "text_prompt_tokens": 1144,
            "total_tokens": 1596
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_40": {
        "status": "generated",
        "case_count": 9,
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
      "e2edev_bench_42": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 3914,
          "output_tokens": 1062,
          "details": {
            "text_prompt_tokens": 3914,
            "total_tokens": 4976
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_44": {
        "status": "generated",
        "case_count": 10,
        "usage": {
          "input_tokens": 1414,
          "output_tokens": 968,
          "details": {
            "text_prompt_tokens": 1414,
            "total_tokens": 2382
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_46": {
        "status": "generated",
        "case_count": 1,
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
      "e2edev_bench_48": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": 1769,
          "output_tokens": 728,
          "details": {
            "text_prompt_tokens": 1769,
            "total_tokens": 2497
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_49": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 1107,
          "output_tokens": 762,
          "details": {
            "text_prompt_tokens": 1107,
            "total_tokens": 1869
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_51": {
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
        "error_stage": null
      },
      "e2edev_bench_52": {
        "status": "generated",
        "case_count": 4,
        "usage": {
          "input_tokens": 1552,
          "output_tokens": 569,
          "details": {
            "text_prompt_tokens": 1552,
            "total_tokens": 2121
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_57": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 1350,
          "output_tokens": 823,
          "details": {
            "text_prompt_tokens": 1350,
            "total_tokens": 2173
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_59": {
        "status": "generated",
        "case_count": 5,
        "usage": {
          "input_tokens": 1567,
          "output_tokens": 597,
          "details": {
            "text_prompt_tokens": 1567,
            "total_tokens": 2164
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_60": {
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
      },
      "e2edev_bench_601": {
        "status": "generated",
        "case_count": 9,
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
      "e2edev_bench_602": {
        "status": "generated",
        "case_count": 10,
        "usage": {
          "input_tokens": 1187,
          "output_tokens": 1025,
          "details": {
            "text_prompt_tokens": 1187,
            "total_tokens": 2212
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_603": {
        "status": "generated",
        "case_count": 6,
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
      "e2edev_bench_63": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 2253,
          "output_tokens": 694,
          "details": {
            "text_prompt_tokens": 2253,
            "total_tokens": 2947
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_64": {
        "status": "generated",
        "case_count": 6,
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
      "e2edev_bench_66": {
        "status": "generated",
        "case_count": 5,
        "usage": {
          "input_tokens": 968,
          "output_tokens": 484,
          "details": {
            "text_prompt_tokens": 968,
            "total_tokens": 1452
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 18,
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
          "input_tokens": 724,
          "output_tokens": 794,
          "details": {
            "text_prompt_tokens": 724,
            "total_tokens": 1518
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_clipboard_and_drag_drop": {
        "status": "generated",
        "case_count": 19,
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
      "firefox_form_manager": {
        "status": "generated",
        "case_count": 8,
        "usage": {
          "input_tokens": 607,
          "output_tokens": 697,
          "details": {
            "text_prompt_tokens": 607,
            "total_tokens": 1304
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_help": {
        "status": "generated",
        "case_count": 27,
        "usage": {
          "input_tokens": 1460,
          "output_tokens": 1754,
          "details": {
            "text_prompt_tokens": 1460,
            "total_tokens": 3214
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_image_and_embedded_content": {
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
      "firefox_media_plugins": {
        "status": "generated",
        "case_count": 6,
        "usage": {
          "input_tokens": 274,
          "output_tokens": 440,
          "details": {
            "text_prompt_tokens": 274,
            "total_tokens": 714
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
          "input_tokens": 576,
          "output_tokens": 549,
          "details": {
            "text_prompt_tokens": 576,
            "total_tokens": 1125
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_printing": {
        "status": "generated",
        "case_count": 23,
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
      "firefox_search": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": 384,
          "output_tokens": 500,
          "details": {
            "text_prompt_tokens": 384,
            "total_tokens": 884
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_sidebar": {
        "status": "generated",
        "case_count": 22,
        "usage": {
          "input_tokens": 1188,
          "output_tokens": 1430,
          "details": {
            "text_prompt_tokens": 1188,
            "total_tokens": 2618
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_text_selection": {
        "status": "generated",
        "case_count": 6,
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
          "input_tokens": 470,
          "output_tokens": 343,
          "details": {
            "text_prompt_tokens": 470,
            "total_tokens": 813
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_toolbar": {
        "status": "generated",
        "case_count": 3,
        "usage": {
          "input_tokens": 283,
          "output_tokens": 222,
          "details": {
            "text_prompt_tokens": 283,
            "total_tokens": 505
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_web_location": {
        "status": "generated",
        "case_count": 9,
        "usage": {
          "input_tokens": 664,
          "output_tokens": 662,
          "details": {
            "text_prompt_tokens": 664,
            "total_tokens": 1326
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
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 14,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover important input partitions such as valid product items, different products, and repeated products being dragged and dropped.",
          "state_transition": "Cover states and transitions related to dragging items from the product list and dropping them into the designated drop area to update the cart display.",
          "decision_table": "Cover condition combinations for summing product prices in the cart and formatting the total price to two decimal places with the correct currency symbol.",
          "use_case": "Cover the user flow of dragging a product, dropping it into the designated area, and verifying that the cart display and total money update accordingly.",
          "error_guessing": "Explore plausible failures such as attempting to drag elements without the draggable attribute or dropping into invalid areas."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_02": {
        "status": "generated",
        "case_count": 24,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Used to partition input behaviors for markdown content such as valid markdown syntax versus invalid markdown syntax (e.g., unmatched asterisks) and notes with content versus notes with no content.",
          "state_transition": "Directly applies to switching between edit mode and view mode, initial creation states, and loading states from local storage where elements toggle visibility.",
          "use_case": "Covers the end-to-end user workflows of adding a note, typing markdown, toggling edit/view modes, persisting data to local storage, and deleting notes.",
          "error_guessing": "Targeted at plausible failure conditions like complex or invalid Markdown input handling, rapid multi-click creation of notes, and empty local storage initialization."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_03": {
        "status": "generated",
        "case_count": 20,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partition inputs and seat statuses into valid available seats, selected seats, occupied non-selectable seats, and different movie price options.",
          "state_transition": "Cover seat states (available, selected, occupied) and transitions when clicking seats, as well as initialization states from local storage.",
          "use_case": "Cover end-to-end user flows involving loading the webpage, selecting movies, selecting and deselecting seats, and persisting data in local storage.",
          "error_guessing": "Explore plausible failure conditions such as attempting to click on occupied seats and handling missing local storage keys."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_04": {
        "status": "generated",
        "case_count": 43,
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
          "equivalence_partitioning": "Cover important input partitions such as valid voice selections, specific language codes, and entered text values in the textarea.",
          "boundary_value_analysis": "Exercise stated limits and boundary conditions including rapid repeated clicks on toggle and phrase buttons.",
          "state_transition": "Cover relevant UI states like hidden and visible text boxes controlled by the 'show' class, as well as the 'voiceschanged' event and active highlight state.",
          "decision_table": "Cover combinations of conditions such as toggling visibility, selecting specific voices, entering text, and clicking the read or close buttons.",
          "combinatorial": "Cover meaningful combinations of multiple requirement factors including different voice options, languages, and interaction sequences.",
          "use_case": "Cover end-to-end user flows like opening the text box, populating voices, selecting a voice, entering text, and reading it aloud.",
          "error_guessing": "Explore plausible failures and misuse such as missing voices, asynchronous API delays, and rapid sequential clicks."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_05": {
        "status": "generated",
        "case_count": 33,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Used to cover normal and abnormal inputs for the search functionality, such as empty search input versus entering a valid word.",
          "boundary_value_analysis": "Required to test the limit on the recent searches list, specifically testing the boundary when the list exceeds five entries and the oldest search is removed.",
          "state_transition": "Used to cover the states and transitions of bookmarking words, toggling the bookmark icon status, opening/closing the offcanvas section, and hiding or showing the result card.",
          "decision_table": "Useful for covering combinations of conditions such as clicking the reset button when the input is empty versus when it contains text and a search has been performed.",
          "use_case": "Covers end-to-end user workflows like entering a search term, viewing details, bookmarking words, managing them in the offcanvas section, and navigating via the 'Back to Top' button.",
          "error_guessing": "Explores plausible failure conditions such as submitting an empty search input or attempting to view bookmarks when no words are bookmarked."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_06": {
        "status": "generated",
        "case_count": 29,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover important input partitions such as valid piano keys, different key types (white and black), and volume slider inputs.",
          "boundary_value_analysis": "Exercise stated limits for the volume slider at its boundaries of 0 (mute) and 1 (maximum volume).",
          "state_transition": "Cover relevant states and transitions such as the 'active' class highlight timing removal after 150ms and checkbox visibility toggles.",
          "decision_table": "Cover combinations of conditions such as checkbox states, rapid toggling, and corresponding label visibility.",
          "use_case": "Cover end-to-end user flows including playing piano keys via mouse clicks and keyboard presses, adjusting volume, and toggling key label visibility.",
          "error_guessing": "Explore plausible failure conditions such as rapid checkbox toggling and handling unexpected or missing sound file paths."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_07": {
        "status": "generated",
        "case_count": 22,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to partition valid numeric inputs for height and weight, and invalid non-numeric or empty inputs that result in NaN.",
          "boundary_value_analysis": "Required to test stated limits and edge scenarios such as minimum non-zero values and maximum reasonable values for height and weight.",
          "use_case": "Required to cover the end-to-end workflow of inputting height and weight, triggering the calculation, and viewing the formatted BMI result.",
          "error_guessing": "Required to test abnormal behavior and plausible failures such as non-numeric characters ('xyz') or empty input fields."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_08": {
        "status": "generated",
        "case_count": 41,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid inputs vs empty fields and valid book genres during form submission.",
          "boundary_value_analysis": "Required to handle edge cases such as unusually long book names as stated in the requirements.",
          "state_transition": "Required to test the navbar toggler expanding/collapsing states and the book issuance/deletion states.",
          "decision_table": "Required to evaluate validation rules such as empty fields, already issued books, and successful issuance conditions.",
          "use_case": "Required to cover end-to-end user flows including adding books, deleting books, and persistence across page reloads.",
          "error_guessing": "Required to target plausible failures like duplicate book issuance and loading empty local storage."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_09": {
        "status": "generated",
        "case_count": 18,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "The requirements define valid inputs (completed fields for schedules and tasks) and invalid inputs (empty fields causing prevention of addition) which must be partitioned.",
          "decision_table": "The requirements specify rules for validating combinations of form fields (Subject, Date, Time for schedules; Task, Deadline for tasks) being empty or filled to determine if the add action succeeds or fails.",
          "use_case": "The requirements describe end-to-end user workflows for filling out forms, submitting them via buttons, verifying list appends, and ensuring form fields reset successfully.",
          "error_guessing": "Plausible failures include submitting forms with partially filled fields (leaving only one or two fields empty) and verifying that the system correctly prevents additions and resets properly."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_10": {
        "status": "generated",
        "case_count": 20,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partitioning is needed to test valid answer selections versus unselected options when advancing to the next question.",
          "state_transition": "The quiz progresses through sequential states of questions and eventually transitions to the final score display state.",
          "decision_table": "Combinations of correctness (correct vs incorrect/no selection) and question advancement determine the score increment and UI visibility.",
          "use_case": "The requirements describe a complete interactive user flow through the quiz portal from initial load to final score.",
          "error_guessing": "Testing scenarios such as clicking 'Next Question' without selecting any option helps uncover plausible handling of empty inputs."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_11": {
        "status": "generated",
        "case_count": 40,
        "usage": {
          "input_tokens": 9500,
          "output_tokens": 4718,
          "details": {
            "text_prompt_tokens": 9500,
            "total_tokens": 14218
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid numeric inputs versus invalid or missing inputs for loan amount, interest rate, and loan term fields.",
          "boundary_value_analysis": "Required to test the stated limits of the loan term slider between 1 and 30, inclusive.",
          "state_transition": "Required to test toggling the dark mode switch on the body element between checked and unchecked states.",
          "decision_table": "Required to handle the combinations of valid/invalid/zero inputs when the calculate button is pressed and determine the resulting action.",
          "use_case": "Required to cover the end-to-end user flow of inputting loan parameters, calculating results, updating charts, and toggling themes.",
          "error_guessing": "Required to explore plausible failure conditions such as 0 interest rate and missing/invalid inputs triggering the 'Please check your numbers' alert."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_12": {
        "status": "generated",
        "case_count": 8,
        "usage": {
          "input_tokens": 2586,
          "output_tokens": 1172,
          "details": {
            "text_prompt_tokens": 2586,
            "total_tokens": 3758
          },
          "status": "available"
        },
        "selected_techniques": [
          "use_case",
          "state_transition",
          "error_guessing"
        ],
        "technique_rationales": {
          "use_case": "The requirements describe distinct end-to-end user workflows: loading the webpage to automatically fetch a joke, and clicking the button to fetch a new joke, replacing the previous content.",
          "state_transition": "The system transitions from displaying placeholder text to displaying an initial joke, and subsequently transitions between different displayed jokes upon user interaction.",
          "error_guessing": "Plausible failures like API fetch failures during page load or button click should be considered to ensure robust handling of external network requests."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_13": {
        "status": "generated",
        "case_count": 16,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid numeric inputs versus invalid or empty inputs in the height input field and covering all dropdown option partitions.",
          "state_transition": "Required to verify changes in visibility and content states (output row, reset button visibility, placeholders, and labels) upon selecting dropdowns, entering values, or clicking reset.",
          "use_case": "Required to cover the end-to-end user flow of selecting conversion units, entering height values, viewing converted results, and resetting the application.",
          "error_guessing": "Required to test unexpected actions such as clicking the reset button when no input or invalid input is present."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_15": {
        "status": "generated",
        "case_count": 42,
        "usage": {
          "input_tokens": 8301,
          "output_tokens": 4509,
          "details": {
            "text_prompt_tokens": 8301,
            "total_tokens": 12810
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partition valid and invalid input or behavior classes for volume, playback rate, and skipping ranges.",
          "boundary_value_analysis": "Exercise boundary values for video duration (0 seconds and maximum duration), volume slider (0 to 1), playback rate (0.5 to 2), and skip limits.",
          "state_transition": "Cover states and transitions for play/pause toggle, fullscreen/normal mode toggling, and rapid click stabilization.",
          "use_case": "Cover end-to-end user flows including playing videos, scrubbing the progress bar, adjusting volume and speed, and toggling fullscreen.",
          "error_guessing": "Explore plausible failure conditions such as rapid clicking on toggle buttons and entering invalid values outside the playback rate range."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_18": {
        "status": "generated",
        "case_count": 42,
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
          "equivalence_partitioning": "Used for partitioning valid and invalid values for the subject text, time formats (00:00-23:59), and day checkbox selections.",
          "boundary_value_analysis": "Applied to test the time picker limits (00:00 and 23:59) and lengths of subject inputs.",
          "state_transition": "Covers the timetable states, updating existing matching time rows versus inserting new rows in chronological order.",
          "decision_table": "Used to evaluate the conditional logic of form submission when required fields are filled, empty, or existing entries match.",
          "combinatorial": "Covers combinations of selected days and time slots.",
          "use_case": "Covers the end-to-end user flow of filling out the timetable form, submitting it, verifying chronological sorting, and form resetting.",
          "error_guessing": "Covers plausible failures like submitting incomplete forms to trigger the alert message."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_19": {
        "status": "generated",
        "case_count": 21,
        "usage": {
          "input_tokens": 4630,
          "output_tokens": 2402,
          "details": {
            "text_prompt_tokens": 4630,
            "total_tokens": 7032
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
          "equivalence_partitioning": "Required to test valid inputs (normal tasks, special characters, tasks with leading/trailing spaces to be trimmed) and invalid inputs (empty tasks or whitespace-only strings).",
          "state_transition": "Required to test the lifecycle of todo items: toggling between completed and uncompleted states, and transitioning from existence to removal.",
          "use_case": "Required to cover end-to-end user flows such as adding a task, persisting it in localStorage, reloading the page, toggling completion, and removing items.",
          "error_guessing": "Required to test plausible failures like handling empty localStorage on page load, suppressing the default context menu on right-click, and invalid JSON in localStorage."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_20": {
        "status": "generated",
        "case_count": 31,
        "usage": {
          "input_tokens": 9440,
          "output_tokens": 3470,
          "details": {
            "text_prompt_tokens": 9440,
            "total_tokens": 12910
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover valid inputs where all fields are filled versus invalid partitions where one or more form fields are empty.",
          "state_transition": "Cover states of the application such as active tabs ('Register a Car' versus 'View All Registrations') and transitions caused by clicking tab buttons and deleting registrations.",
          "decision_table": "Cover combinations of form completion conditions and their resulting actions, such as saving to localStorage, resetting the form, or displaying an alert.",
          "use_case": "Cover end-to-end user workflows involving navigating between tabs, filling out forms, submitting data, viewing stored records in tables, and deleting entries.",
          "error_guessing": "Explore plausible failure conditions such as submitting incomplete forms, clicking tab buttons multiple times, and handling empty localStorage states."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_21": {
        "status": "generated",
        "case_count": 27,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "state_transition",
          "equivalence_partitioning",
          "use_case",
          "decision_table"
        ],
        "technique_rationales": {
          "state_transition": "The requirements describe distinct states of the music player (playing vs. paused) and transitions triggered by clicking the play button, previous/next buttons, and song completion.",
          "equivalence_partitioning": "Inputs and navigation boundaries such as normal songs, the first song (looping to last), and the last song (looping to first) form distinct partitions for playlist navigation.",
          "use_case": "The requirements describe continuous music playback flows including navigation through playlists and automatic transition on song completion.",
          "decision_table": "The play/pause button behavior depends on multiple combined conditions including the presence of the 'play' class on the container and the icon class of the button."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_22": {
        "status": "generated",
        "case_count": 33,
        "usage": {
          "input_tokens": 13820,
          "output_tokens": 5358,
          "details": {
            "text_prompt_tokens": 13820,
            "total_tokens": 19178
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partitioning the user voting status into classes where 'hasVoted' is absent versus present in localStorage to test normal voting behavior and duplicate vote prevention.",
          "state_transition": "Covering the core state changes of the application, including initial states, voted states, reset states, and the visibility states of the detailed results section.",
          "decision_table": "Evaluating the combinations of conditions such as user click actions on different candidates (A, B, C), reset buttons, show results buttons, and the presence of the 'hasVoted' flag leading to specific actions and alerts.",
          "use_case": "Covering complete user flows from casting a vote, viewing detailed breakdowns, resetting votes, and attempting subsequent actions.",
          "error_guessing": "Exploring plausible failure modes like attempting to vote multiple times when 'hasVoted' is set to true in localStorage and ensuring the system handles it gracefully with alerts."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_24": {
        "status": "generated",
        "case_count": 38,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid positive numerical partitions and invalid partitions like negative numbers, non-numeric strings, and empty fields for all input fields.",
          "boundary_value_analysis": "Needed to test limits and edges like zero, minimum valid decimal values (e.g., 0.01), and minimum integer values (e.g., 1 for compounding frequency).",
          "decision_table": "Required to evaluate combinations of validation conditions across multiple input fields simultaneously when triggering the calculate action.",
          "use_case": "Needed to cover end-to-end flows of interacting with the compound interest calculator, filling out fields, triggering via button click or Enter key, and viewing results.",
          "error_guessing": "Useful to anticipate plausible failures such as missing inputs, invalid character entry, and handling alert messages correctly."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_25": {
        "status": "generated",
        "case_count": 33,
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
          "equivalence_partitioning": "Partition valid double-clicks inside the image container versus invalid single clicks or double-clicks outside the container.",
          "boundary_value_analysis": "Test double-clicks near the boundaries of the image area and timing limits such as intervals approaching or exceeding 800 milliseconds.",
          "state_transition": "Cover states of the heart icon appearance, the 1-second timeout removal from the DOM, and increments to the like count.",
          "decision_table": "Cover combinations of conditions including click counts, click locations (inside vs outside), and timing intervals for double-clicks.",
          "combinatorial": "Cover combinations of rapid consecutive double-clicks and boundary positions to verify correct multi-icon creation and offset calculations.",
          "use_case": "Cover the end-to-end user flow of interacting with the image container to display hearts, update like counts, and observe instruction text.",
          "error_guessing": "Explore plausible failure conditions such as rapid consecutive clicks, overlapping timeouts, and misplaced clicks outside the image container."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_26": {
        "status": "generated",
        "case_count": 29,
        "usage": {
          "input_tokens": 10910,
          "output_tokens": 3651,
          "details": {
            "text_prompt_tokens": 10910,
            "total_tokens": 14561
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
          "equivalence_partitioning": "Used to partition input text values into valid inputs, empty inputs, non-existent search/replace terms, and exact matches versus substrings.",
          "state_transition": "Used to model the visibility states of the sub-list (hidden/block) and the active tabs ('search' and 'replace') triggered by user interactions on expand, search, and replace list items.",
          "use_case": "Used to test the end-to-end user workflows for expanding menus, selecting search or replace features, inputting text, and executing operations.",
          "error_guessing": "Used to cover plausible failure conditions such as clicking replace without expanding the list first, leaving input fields empty, or searching/replacing text that does not exist in the paragraph."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_27": {
        "status": "generated",
        "case_count": 33,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid keywords, empty keywords, whitespace-only inputs, and terms that yield no matching search results.",
          "state_transition": "Required to manage changes in state between initial page load, successful search results, empty search outcomes, and selecting a specific meal.",
          "decision_table": "Required to test combinations of search input conditions (valid text, empty, whitespace) and their respective UI updates across containers and headings.",
          "use_case": "Required to cover end-to-end user workflows such as searching for meals, clicking a meal result for details, and triggering random meals.",
          "error_guessing": "Required to handle plausible failures like API request failures during random meal fetching or rapid clicking on the random button."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_28": {
        "status": "generated",
        "case_count": 36,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partitioning the board tile states into valid empty tiles for clicking and invalid occupied tiles, as well as game states into active, win, and tie conditions.",
          "boundary_value_analysis": "Exercising minimum moves to win and the final move resulting in a tie to cover boundary conditions of the game board.",
          "state_transition": "Covering the game states (active turn-taking, win state, tie state, and resetting back to initial state) and transitions caused by user clicks.",
          "decision_table": "Handling combinations of conditions such as whether a tile is empty or occupied when clicked and whether the game is active or inactive.",
          "use_case": "Covering end-to-end user flows of playing a complete game of Tic Tac Toe from initialization through moves to a win, tie, and reset.",
          "error_guessing": "Targeting plausible failures like clicking already occupied tiles or attempting to interact with the board after a win or tie has been announced."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_29": {
        "status": "generated",
        "case_count": 46,
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
          "equivalence_partitioning": "Used to partition input values into valid categories (positive amounts for income, negative amounts for expenses, zero, non-empty descriptions) and invalid categories (empty description, empty amount, invalid non-numerical amount data).",
          "boundary_value_analysis": "Used to test inputs at the boundaries of valid data, such as empty fields, very long descriptions, and zero or near-zero amounts.",
          "state_transition": "Used to cover the lifecycle states of the application starting from empty local storage initialization, moving to populated states upon adding transactions, and returning to empty states or recalculated values upon removing transactions.",
          "decision_table": "Used to evaluate combinations of validation conditions for the description and amount input fields when the 'Add Transaction' button is clicked and the corresponding success or alert outcomes.",
          "combinatorial": "Used to test combinations of multiple transaction types (income and expense entries) to verify that balance, income, and expense totals compute correctly.",
          "use_case": "Used to cover the end-to-end user workflows of loading the application, entering transaction details, adding transactions to the history list, persisting them in localStorage, and removing transactions.",
          "error_guessing": "Used to target plausible failures like malformed local storage data, missing keys, and invalid submission attempts."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_30": {
        "status": "generated",
        "case_count": 23,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover valid inputs (fully filled form fields, 'Attendee' and 'VIP' options) vs invalid inputs (empty fields).",
          "boundary_value_analysis": "Test minimum input lengths and edge cases such as large text content mentioned in the requirements.",
          "state_transition": "Cover the transition from the form container visible state to the badge container visible state upon submission.",
          "decision_table": "Cover combinations of required form fields being filled or left empty to determine if the form hides and the badge appears.",
          "use_case": "Cover the end-to-end user flow of filling out the form, generating the badge with a QR code, and downloading it as a PNG image.",
          "error_guessing": "Explore plausible failure conditions such as submitting with missing required fields or encountering download errors."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_32": {
        "status": "generated",
        "case_count": 23,
        "usage": {
          "input_tokens": 8170,
          "output_tokens": 2768,
          "details": {
            "text_prompt_tokens": 8170,
            "total_tokens": 10938
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
          "equivalence_partitioning": "Required to test valid task descriptions (non-empty, trimmed) and invalid task descriptions (empty, consisting solely of whitespace).",
          "state_transition": "Required to test states such as task completion toggling, task addition/deletion, and the conditional visibility of the 'Clear All' button based on task list state.",
          "use_case": "Required to cover end-to-end user workflows including entering tasks via button click or Enter key, updating task statuses, deleting tasks, and clearing all tasks.",
          "error_guessing": "Required to test edge cases such as deleting the only remaining task in the list and attempting to add empty or whitespace-only inputs."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_36": {
        "status": "generated",
        "case_count": 26,
        "usage": {
          "input_tokens": 6369,
          "output_tokens": 3089,
          "details": {
            "text_prompt_tokens": 6369,
            "total_tokens": 9458
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover important input partitions such as empty input, input with only spaces/newlines, normal text, and special characters for word, character, and paragraph calculations.",
          "boundary_value_analysis": "Exercise stated limits such as large texts up to 5000 characters and the custom character limit set via the char-limit input.",
          "state_transition": "Cover relevant states like entering text, clicking count/clear buttons, exceeding character limits, and persisting or reloading state via localStorage.",
          "use_case": "Cover the end-to-end user workflows involving typing text, calculating counts, setting limits, highlighting words, clearing fields, and page refresh persistence.",
          "error_guessing": "Explore plausible failure conditions such as clearing an already empty input field and handling edge cases with whitespace and newlines."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_37": {
        "status": "generated",
        "case_count": 19,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Used to partition input text conditions into empty and non-empty classes for the textarea.",
          "boundary_value_analysis": "Used to test the stated maximum length limit of 280 characters for text input.",
          "state_transition": "Used to cover the sequential progress states of the progress bar items and button background color changes during transfer.",
          "decision_table": "Used to cover combinations of conditions such as textarea state (empty vs non-empty) and the resulting actions (alert vs text transfer).",
          "use_case": "Used to cover the end-to-end user workflow of entering text, clicking the button, observing progress indicators, and clearing the textarea.",
          "error_guessing": "Used to explore plausible failure conditions such as clicking the transfer button when the textarea is empty."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_40": {
        "status": "generated",
        "case_count": 43,
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
          "equivalence_partitioning": "Used to partition valid and invalid input classes for the password length and character selection checkboxes.",
          "boundary_value_analysis": "Required to test the stated limits of the password length input field (minimum of 4 and maximum of 20).",
          "state_transition": "Applicable for managing the persistent toggle states of checkboxes (uppercase, lowercase, numbers, symbols) and clipboard notification timeout states.",
          "decision_table": "Useful for covering combinations of character type checkbox selections (none selected, some selected, all selected) and their conditional action on password generation.",
          "combinatorial": "Used to test meaningful combinations of multiple criteria checkboxes and length settings during password generation.",
          "use_case": "Covers the end-to-end user workflow of specifying criteria, generating a password, and copying it to the clipboard.",
          "error_guessing": "Explores plausible failure scenarios such as clicking copy to clipboard when no password has been generated or trying to generate a password with no criteria selected."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_42": {
        "status": "generated",
        "case_count": 47,
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
          "equivalence_partitioning": "Used to partition input fields into valid positive numbers, zero, missing inputs, and negative numbers across salary, hours, workdays, tax percentages, and overtime rates.",
          "boundary_value_analysis": "Applicable for testing values at and around limits, specifically checking behavior at zero for work hours, workdays, gross salary, tax percentages, and overtime values.",
          "state_transition": "Used to verify form states, specifically transitions between default unpopulated states, calculated result states, and the reset state triggered by the 'Clear' button.",
          "decision_table": "Required to handle combinations of input conditions such as various combinations of gross salary, tax percentage, and overtime hours determining tax deductions and total earnings.",
          "combinatorial": "Useful for covering meaningful combinations of multiple numeric salary parameters and job inputs entered simultaneously before hitting the calculate button.",
          "use_case": "Covers end-to-end workflows including entering job details and salary parameters, clicking calculate, verifying multiple dependent results, and resetting via the clear button.",
          "error_guessing": "Explores plausible failure conditions and misuse such as negative salaries, negative tax rates, negative overtime hours, and extremely long or special-character job titles."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_44": {
        "status": "generated",
        "case_count": 32,
        "usage": {
          "input_tokens": 7490,
          "output_tokens": 3261,
          "details": {
            "text_prompt_tokens": 7490,
            "total_tokens": 10751
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
          "equivalence_partitioning": "Partition valid number sequences, operator sequences, and invalid expressions (such as empty display on equals or division by zero).",
          "state_transition": "Cover the calculator display states, clearing behavior, theme toggling states, and consecutive operator replacements.",
          "use_case": "Cover end-to-end user workflows like inputting arithmetic expressions with numbers, operators, and parentheses, and evaluating them.",
          "error_guessing": "Explore plausible user errors such as clicking backspace on an empty display or clicking the equal button with an empty display."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_46": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover the different days of the week from Sunday to Saturday as valid partitions for date settings to ensure correct day name and quote mapping.",
          "boundary_value_analysis": "Test the boundary days of the week, specifically Sunday and Saturday, to ensure the local date setting edge cases are handled correctly.",
          "use_case": "Cover the end-to-end page load flow where the application automatically determines the day and updates the designated UI elements without user interaction.",
          "error_guessing": "Explore plausible failures such as unexpected local date formats or invalid system clock values affecting the automatic determination of the weekday."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_48": {
        "status": "generated",
        "case_count": 31,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Valid and invalid partitions for car selection, rental days (e.g. minimum 1), and calculation status are defined across the requirements.",
          "boundary_value_analysis": "Requirements specify a minimum limit of 1 day for rental days and mention edge cases such as maximum integer values for days.",
          "state_transition": "The system transitions between different car choices, resetting total prices, calculating totals, and moving to booking states.",
          "decision_table": "Form submission and calculation behaviors depend on combinations of conditions like car selected, total price calculated, and rental days validity.",
          "use_case": "The requirements describe an end-to-end car rental user flow from selecting a model, entering days, calculating total, to final booking.",
          "error_guessing": "Plausible failure scenarios such as submitting without selecting a car, zero or missing days, and submitting without calculating total price must be tested."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_49": {
        "status": "generated",
        "case_count": 18,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partition valid and invalid classes for student name and grade inputs (e.g., valid names vs empty names, valid grades 0-100 vs invalid grades below 0 or above 100).",
          "boundary_value_analysis": "Exercise grade limits and boundaries explicitly mentioned in the requirements, specifically at 0, 100, and immediately outside the limits such as -1 and 101.",
          "use_case": "Cover the end-to-end user flow of filling out the student grade book form, submitting valid data, appending to the student list, and resetting the form.",
          "error_guessing": "Explore plausible user errors and failure conditions such as submitting empty fields or out-of-range grades, verifying that submission is blocked and values are retained."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_51": {
        "status": "generated",
        "case_count": 34,
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
          "equivalence_partitioning": "Cover equivalence partitions for difficulty levels (Easy, Medium, Hard), correct versus incorrect typed words, and localStorage persistence states.",
          "boundary_value_analysis": "Test limits such as the game ending when the timer reaches zero and handling rapid consecutive clicks on the settings button.",
          "state_transition": "Cover the form visibility toggle states, game states (active gameplay versus end-game container display), and transitions triggered by correct word entries or timer expiration.",
          "decision_table": "Cover the combination of conditions including typed word correctness and different difficulty levels determining the specific time increments (5s, 3s, 2s).",
          "combinatorial": "Cover combinations of difficulty settings stored in localStorage and various initial states upon page load.",
          "use_case": "Cover the end-to-end user flow of loading the page, configuring settings, typing words correctly to increment score and time, and reaching the end-game state.",
          "error_guessing": "Explore plausible failure conditions such as missing localStorage keys, empty inputs, and rapid consecutive clicks on interface elements."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_52": {
        "status": "generated",
        "case_count": 22,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Used to partition valid active circle indices and progress percentage ranges.",
          "boundary_value_analysis": "Used to test limits such as the first step (circle 1) and the last step (circle 4), as well as minimum and maximum progress bar widths.",
          "state_transition": "Used to model transitions between progress steps and corresponding button enable/disable states.",
          "use_case": "Used to cover the end-to-end user workflow of navigating forward and backward through the progress steps.",
          "error_guessing": "Used to handle edge cases and plausible misuse like rapid clicking on the 'Prev' or 'Next' buttons beyond the first and last circles."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_57": {
        "status": "generated",
        "case_count": 28,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partition input checkbox states into groups such as all checked, none checked, and a mixed state of some checked and some unchecked.",
          "state_transition": "Manage the state changes of the 'Select All/None' checkbox, its label text ('全选' vs '全不选'), and individual checkboxes based on user actions like clicking select all, individual toggling, or reverse selection.",
          "decision_table": "Determine the resulting actions and states of the master checkbox and its label under various combinations of individual checkbox selection states.",
          "use_case": "Cover the end-to-end user workflows involving bulk selection, manual individual toggling, and selection inversion via the reverse link.",
          "error_guessing": "Explore plausible edge cases like toggling individual checkboxes until all are selected or deselected to verify dynamic master checkbox synchronization."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_59": {
        "status": "generated",
        "case_count": 25,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partition valid and invalid input or behavior classes, such as selecting an answer option versus selecting no option before submission.",
          "state_transition": "Cover relevant states, events, and transitions through the quiz questions, answer evaluations, score display, and page reset via the Play Again button.",
          "decision_table": "Cover combinations of conditions like submitting with an answer selected vs. no answer selected, and correct vs. incorrect answers.",
          "use_case": "Cover the end-to-end user flow of loading the quiz, answering questions sequentially, viewing the final score, and restarting the quiz.",
          "error_guessing": "Explore plausible failures such as rapid or repeated clicks on radio buttons, and attempting to submit without selecting any answer."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_60": {
        "status": "generated",
        "case_count": 29,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test important input partitions such as normal input amounts, zero values, and very large numbers in the amount field.",
          "boundary_value_analysis": "Required to test stated limits and edge cases such as inputting zero or edge conditions where both selected currencies are identical.",
          "state_transition": "Required to cover states and transitions involving dropdown changes, default initialization (USD to EUR), and currency swapping.",
          "use_case": "Required to cover end-to-end user flows including selecting currencies, typing amounts, swapping currencies, and dynamic recalculations.",
          "error_guessing": "Required to address plausible failures such as external API fetch issues and edge cases like identical currency selections."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_601": {
        "status": "failed",
        "case_count": 16,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Valid and invalid partitions for input fields like 'Bill Amount', 'Custom Tip', and 'Number of People' are explicitly mentioned in the requirements.",
          "boundary_value_analysis": "Limits and thresholds such as numeric values greater than zero for the bill amount and number of people require boundary checking.",
          "state_transition": "The UI components transition between enabled, disabled, selected, and deselected states based on user inputs and clicks.",
          "decision_table": "Enabling the 'Generate Bill' button depends on combinations of conditions such as valid bill amount, presence of a tip, and number of people.",
          "use_case": "The requirements describe end-to-end user workflows from entering a bill amount, selecting tips, generating a bill, to resetting the form.",
          "error_guessing": "Negative numbers, empty fields, non-numeric inputs, and interacting with disabled tip containers are plausible failure and misuse scenarios."
        },
        "error_type": "ModelUnavailableError",
        "error_stage": "ghl_generate_state_transition"
      },
      "e2edev_bench_602": {
        "status": "generated",
        "case_count": 30,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid positive/negative numerical inputs as well as invalid non-numerical inputs for both 'Min' and 'Max' fields.",
          "boundary_value_analysis": "Necessary for testing cases where 'Min' equals 'Max', 'Min' is greater than 'Max', and edge cases like zero.",
          "state_transition": "Applies to testing the copy-to-clipboard button state transition from 'Copy to Clipboard' to 'Copied!' and back after 2000 milliseconds.",
          "use_case": "Covers the end-to-end user flow of loading the app, setting ranges, clicking generate, observing the scaling display, and copying to the clipboard.",
          "error_guessing": "Helps target plausible failures such as entering invalid text strings or edge ranges where min and max behave unexpectedly."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_603": {
        "status": "generated",
        "case_count": 12,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "boundary_value_analysis",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partition inputs into valid digits, non-numeric characters, zero, and numbers exceeding 15 digits.",
          "boundary_value_analysis": "Test values around the 15-digit limit and zero input to ensure correct boundary handling.",
          "error_guessing": "Explore plausible user errors such as entering letters or symbols and extremely large numbers."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_63": {
        "status": "generated",
        "case_count": 32,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid positive integers, zero, negative integers, and invalid non-numeric inputs for the LCM and HCF input fields.",
          "boundary_value_analysis": "Required to test edge cases such as both fields containing the same number, one field containing zero, or one field containing negative numbers.",
          "state_transition": "Required to test the visibility toggle states and transitions of the LCM and HCF forms when their respective buttons are clicked.",
          "decision_table": "Required to test the logic combinations for even and odd result parities and their corresponding opacity indicator changes.",
          "use_case": "Required to cover end-to-end user workflows from loading the page, toggling forms, inputting numbers, calculating LCM/HCF, to viewing results and opacity indicators.",
          "error_guessing": "Required to test plausible failures like submitting empty input fields or entering invalid non-numeric characters."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_64": {
        "status": "failed",
        "case_count": 0,
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
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "The requirements define partitions for guesses (empty, correct, too high, too low) and score handling (positive score, score reaching zero).",
          "boundary_value_analysis": "The requirements explicitly specify the range limits for the secret number and inputs (between 1 and 20, edge cases 1 and 20).",
          "state_transition": "The application manages specific game states such as initial state, playing, winning, losing, and resetting via the 'Again!' button.",
          "decision_table": "The checking mechanism evaluates multiple conditions including empty inputs, high/low/correct guesses, and highscore updates to trigger respective UI actions.",
          "use_case": "The requirements outline complete interactive user flows from entering guesses and receiving feedback to winning, losing, and restarting the game.",
          "error_guessing": "Plausible failures like submitting empty inputs, exhausting all attempts until the score hits zero, and entering out-of-range values can be tested."
        },
        "error_type": "ModelUnavailableError",
        "error_stage": "ghl_generate_equivalence_partitioning"
      },
      "e2edev_bench_66": {
        "status": "generated",
        "case_count": 17,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid inputs (comma-separated choices), edge cases (extra spaces, single entries), and invalid/abnormal inputs (only commas, empty input).",
          "state_transition": "Required to test the sequence of states from typing choices, pressing Enter, executing the 3-second selection animation (30 iterations at 100ms), to ending at the final selected tag state.",
          "use_case": "Required to test the end-to-end user workflow: loading page with automatic focus, typing choices, pressing Enter, clearing textarea, cycling highlights, and concluding with a final selection.",
          "error_guessing": "Required to address plausible failure modes such as attempting to trigger selection with empty input or only special characters and commas."
        },
        "error_type": null,
        "error_stage": null
      },
      "firefox_bookmarks": {
        "status": "failed",
        "case_count": 76,
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
          "equivalence_partitioning": "Required to test valid and invalid classes of bookmark locations, inputs, and viewing operations such as negative view properties.",
          "boundary_value_analysis": "Useful for testing resizable columns and batch deletions around minimum and maximum limits.",
          "state_transition": "Required for managing bookmark hierarchy states, additions, deletions, folders, and persistence across restarts.",
          "decision_table": "Appropriate for handling complex conditions related to sorting, columns visibility, and keyword searches.",
          "combinatorial": "Needed for testing combinations of properties across bookmarks, folders, and separators.",
          "use_case": "Applicable for end-to-end flows like adding, launching via double-click, modifying, and searching bookmarks.",
          "error_guessing": "Essential for plausible failure scenarios such as dropping a bookmark onto itself or handling application crashes."
        },
        "error_type": "ModelUnavailableError",
        "error_stage": "ghl_generate_use_case"
      },
      "firefox_browser_history": {
        "status": "generated",
        "case_count": 54,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "decision_table",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Cover normal and abnormal behavior as well as important input partitions for history groups, deletion of single vs multiple entries, and column show/hide states.",
          "state_transition": "Cover states and transitions such as recording visited links, server redirects, creating session files on restart, and clearing the global history.",
          "decision_table": "Cover condition combinations for sorting, grouping by Day/Site/None, and column visibility/resizing configurations.",
          "use_case": "Cover user flows such as launching history links in a browser window, navigating via Back/Forward dropdowns, and managing history entries.",
          "error_guessing": "Cover plausible failures such as handling empty session history files, failed deletions, and abnormal redirection behaviors."
        },
        "error_type": null,
        "error_stage": null
      },
      "firefox_clipboard_and_drag_drop": {
        "status": "failed",
        "case_count": 47,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test important input partitions such as different content types (text, links, images, directories, files, shortcuts, and non-copyable widgets) dragged or copied across various sources and targets.",
          "state_transition": "Applicable for handling states and transitions when dragging items between different window types, framesets, desktop, editor windows, and dialogs.",
          "use_case": "Needed to cover end-to-end user flows for clipboard operations and drag-and-drop actions between browser windows, desktop, dialog boxes, and external applications.",
          "error_guessing": "Required to explore plausible failures and misuse, such as attempting to copy non-copyable UI widgets or dragging unsupported file types onto the browser window."
        },
        "error_type": "ModelRateLimitError",
        "error_stage": "ghl_generate_error_guessing"
      },
      "firefox_form_manager": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_help": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_image_and_embedded_content": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_media_plugins": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_printing": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_search": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_sidebar": {
        "status": "failed",
        "case_count": 18,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "boundary_value_analysis",
          "state_transition",
          "error_guessing",
          "use_case"
        ],
        "technique_rationales": {
          "boundary_value_analysis": "Required to test the maximum width limit of the sidebar which is approximately one third of the browser window size.",
          "state_transition": "Required to cover sidebar open and close states with grippy, and panel states such as added, deleted, reordered, and saved/cancelled.",
          "error_guessing": "Required to test abnormal behavior and plausible failures such as attempting to add an already added panel.",
          "use_case": "Required to cover user flows involving listing, previewing, adding, customizing, reordering, and deleting panels."
        },
        "error_type": "ModelRateLimitError",
        "error_stage": "ghl_generate_use_case"
      },
      "firefox_text_selection": {
        "status": "failed",
        "case_count": 0,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "use_case",
          "error_guessing"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to partition input behaviors such as starting selections from dead space versus from within text, and normal versus abnormal gesture types.",
          "use_case": "Required to cover end-to-end user flows for various text selection gestures including drag-selection, double-click, shift-select, and drag-scrolling.",
          "error_guessing": "Required to explore plausible failures and incorrect gesture handlings during drag-scrolling and text selection."
        },
        "error_type": "ModelRateLimitError",
        "error_stage": "ghl_generate_equivalence_partitioning"
      },
      "firefox_themes": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_toolbar": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      },
      "firefox_web_location": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": null
      }
    },
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_02": {
        "status": "failed",
        "case_count": 5,
        "usage": {
          "input_tokens": null,
          "output_tokens": null,
          "details": null,
          "status": "unavailable"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": "ModelRateLimitError",
        "error_stage": "critic"
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
        "error_type": "ModelRateLimitError",
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_05": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_06": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_07": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_08": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_09": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_10": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "generator"
      },
      "e2edev_bench_11": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_12": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_13": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_15": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_18": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_19": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_20": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_21": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_22": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_24": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_25": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_26": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_27": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_28": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_29": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_30": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_32": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_36": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_37": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_40": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_42": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_44": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_46": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_48": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_49": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_51": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_52": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_57": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_59": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_60": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_601": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_602": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_603": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_63": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_64": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "e2edev_bench_66": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
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
        "error_type": "ModelRateLimitError",
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_clipboard_and_drag_drop": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_form_manager": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_help": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_image_and_embedded_content": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_media_plugins": {
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
        "error_type": "ModelRateLimitError",
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_printing": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_search": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_sidebar": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_text_selection": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_themes": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_toolbar": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      },
      "firefox_web_location": {
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
        "error_type": "ModelRateLimitError",
        "error_stage": "analyst"
      }
    }
  }
}
```
