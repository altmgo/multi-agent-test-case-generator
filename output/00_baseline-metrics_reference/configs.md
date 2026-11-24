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
    "firefox_themes",
    "firefox_browser_history",
    "firefox_password_manager",
    "firefox_bookmarks",
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
    "one-shot": "batch",
    "GHL": "per_requirement",
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
    "one-shot": {
      "firefox_themes": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": 470,
          "output_tokens": 502,
          "details": {
            "text_prompt_tokens": 470,
            "total_tokens": 972
          },
          "status": "available"
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
          "output_tokens": 793,
          "details": {
            "text_prompt_tokens": 724,
            "total_tokens": 1517
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
          "output_tokens": 430,
          "details": {
            "text_prompt_tokens": 576,
            "total_tokens": 1006
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
          "input_tokens": 1024,
          "output_tokens": 1287,
          "details": {
            "text_prompt_tokens": 1024,
            "total_tokens": 2311
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
          "output_tokens": 411,
          "details": {
            "text_prompt_tokens": 641,
            "total_tokens": 1052
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
        "case_count": 9,
        "usage": {
          "input_tokens": 1271,
          "output_tokens": 525,
          "details": {
            "text_prompt_tokens": 1271,
            "total_tokens": 1796
          },
          "status": "available"
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
          "output_tokens": 645,
          "details": {
            "text_prompt_tokens": 1320,
            "total_tokens": 1965
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
        "case_count": 8,
        "usage": {
          "input_tokens": 1360,
          "output_tokens": 719,
          "details": {
            "text_prompt_tokens": 1360,
            "total_tokens": 2079
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
      "firefox_themes": {
        "status": "generated",
        "case_count": 34,
        "usage": {
          "input_tokens": 11508,
          "output_tokens": 3091,
          "details": {
            "text_prompt_tokens": 11508,
            "total_tokens": 14599
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Partition valid theme choices (Classic and Modern) and menu items available under the View menu.",
          "state_transition": "Cover the states and transitions associated with switching between themes under theme preferences.",
          "use_case": "Cover the user flow of navigating the View menu to access theme preferences and selecting themes."
        },
        "error_type": null,
        "error_stage": null
      },
      "firefox_browser_history": {
        "status": "generated",
        "case_count": 153,
        "usage": {
          "input_tokens": 46884,
          "output_tokens": 14299,
          "details": {
            "text_prompt_tokens": 46884,
            "total_tokens": 61183
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
          "equivalence_partitioning": "Required to test normal and abnormal recording of visited links, grouping modes (Day, Site, None), and sorting options.",
          "state_transition": "Required for tracking history lifecycle events such as recording links, server redirects, deleting single or multiple entries, clearing history, and session history file creation.",
          "decision_table": "Required to test combinations of column visibility, resizable limits, and grouping/sorting conditions.",
          "use_case": "Required to test end-to-end user workflows involving navigating via Back and Forward button dropdowns, clicking history items to launch browser windows, and managing history entries.",
          "error_guessing": "Used to anticipate plausible failures during deletion of multiple history entries, clearing global history, and handling redirects."
        },
        "error_type": null,
        "error_stage": null
      },
      "firefox_password_manager": {
        "status": "generated",
        "case_count": 54,
        "usage": {
          "input_tokens": 18145,
          "output_tokens": 5667,
          "details": {
            "text_prompt_tokens": 18145,
            "total_tokens": 23812
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
          "equivalence_partitioning": "Required to test important input partitions such as saving passwords, selecting 'Never For This Site', and having multiple credentials.",
          "state_transition": "Required to handle states such as enabled/disabled preferences, stored credentials, changed passwords, and deleted credentials.",
          "use_case": "Required to cover end-to-end user flows like prompting to save, changing passwords, viewing preferences, and autofilling.",
          "error_guessing": "Required to explore plausible failures such as improper removal or handling of disabled password manager states."
        },
        "error_type": null,
        "error_stage": null
      },
      "firefox_bookmarks": {
        "status": "generated",
        "case_count": 227,
        "usage": {
          "input_tokens": 97128,
          "output_tokens": 21006,
          "details": {
            "text_prompt_tokens": 97128,
            "total_tokens": 118134
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
          "equivalence_partitioning": "Partitioning valid and invalid operations such as dropping a bookmark onto itself versus valid locations, and viewing properties for valid versus invalid items.",
          "state_transition": "Covering the lifecycle states and transitions of bookmarks, folders, and separators being added, modified, renamed, and deleted across restarts and crashes.",
          "decision_table": "Covering combinations of conditions for column sorting, visibility, resizing, and property actions.",
          "use_case": "Covering user flows such as launching bookmarks via double-clicking, inline renaming, searching by keywords, and managing items in the personal toolbar.",
          "error_guessing": "Exploring plausible failure conditions and misuse such as browser crashes during save operations and prohibited drop actions onto immediate parents or children."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_01": {
        "status": "generated",
        "case_count": 48,
        "usage": {
          "input_tokens": 13333,
          "output_tokens": 5914,
          "details": {
            "text_prompt_tokens": 13333,
            "total_tokens": 19247
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
          "equivalence_partitioning": "Partition product item inputs and cart contents into valid and invalid classes for adding items and calculating total prices.",
          "boundary_value_analysis": "Test formatting and quantity limits such as single and repeated product additions, and two decimal place currency rounding limits.",
          "state_transition": "Cover the states and transitions of product items being dragged, dropped into the drop area, and updating the cart display and total price.",
          "decision_table": "Combine conditions such as adding different versus repeated products and verify resulting actions on cart quantities, unit prices, and titles.",
          "use_case": "Cover the end-to-end user flow of dragging a product from the list, dropping it into the designated drop area, and verifying the updated cart display and total price.",
          "error_guessing": "Explore plausible failures such as dragging non-draggable elements or dropping outside the designated drop area."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_02": {
        "status": "generated",
        "case_count": 52,
        "usage": {
          "input_tokens": 27958,
          "output_tokens": 5731,
          "details": {
            "text_prompt_tokens": 27958,
            "total_tokens": 33689
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
          "equivalence_partitioning": "Used to partition valid inputs like correct markdown syntax and invalid/malformed markdown inputs.",
          "state_transition": "Used to cover the note states between view mode and edit mode, and their transitions triggered by the edit button.",
          "use_case": "Used to cover complete user flows such as creating a note, typing markdown, switching modes, and deleting a note.",
          "error_guessing": "Used to handle plausible failures like invalid markdown inputs and interactions with empty local storage."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_03": {
        "status": "generated",
        "case_count": 49,
        "usage": {
          "input_tokens": 22152,
          "output_tokens": 5281,
          "details": {
            "text_prompt_tokens": 22152,
            "total_tokens": 27433
          },
          "status": "available"
        },
        "selected_techniques": [
          "equivalence_partitioning",
          "state_transition",
          "use_case"
        ],
        "technique_rationales": {
          "equivalence_partitioning": "Required to test valid and invalid classes for seat selection (available vs occupied) and movie ticket prices.",
          "state_transition": "Required to test seat status changes between available, selected, and occupied, as well as persistence via local storage states.",
          "use_case": "Required to cover the end-to-end user workflow of opening the booking page, selecting movies, selecting and deselecting seats, and calculating totals."
        },
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_04": {
        "status": "generated",
        "case_count": 137,
        "usage": {
          "input_tokens": 60774,
          "output_tokens": 14579,
          "details": {
            "text_prompt_tokens": 60774,
            "total_tokens": 75353
          },
          "status": "available"
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
          "equivalence_partitioning": "Cover important input partitions such as valid voice selections, specific language codes (e.g., 'CN', 'US'), and text entries.",
          "boundary_value_analysis": "Exercise stated limits and boundary conditions such as rapid repeated clicks on toggle and phrase boxes.",
          "state_transition": "Cover visibility states of the text box (controlled by the 'show' class) and transitions triggered by toggle and close buttons.",
          "decision_table": "Cover condition combinations for populating voices, handling the 'voiceschanged' event, and selecting active voices for speech synthesis.",
          "combinatorial": "Cover meaningful combinations of multiple requirement factors like selecting different voices and entering text simultaneously.",
          "use_case": "Cover end-to-end user flows including opening the text box, selecting a voice, entering text, clicking 'Read Text', and clicking predefined phrase boxes.",
          "error_guessing": "Explore plausible failures such as missing voices during initialization or rapid sequential clicks across different phrase and toggle buttons."
        },
        "error_type": null,
        "error_stage": null
      }
    },
    "Multiagent": {
      "firefox_themes": {
        "status": "generated",
        "case_count": 7,
        "usage": {
          "input_tokens": 50529,
          "output_tokens": 4314,
          "details": {
            "text_prompt_tokens": 50529,
            "total_tokens": 54843
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "firefox_browser_history": {
        "status": "generated",
        "case_count": 30,
        "usage": {
          "input_tokens": 28179,
          "output_tokens": 3775,
          "details": {
            "text_prompt_tokens": 28179,
            "total_tokens": 31954
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
        "case_count": 13,
        "usage": {
          "input_tokens": 12800,
          "output_tokens": 1988,
          "details": {
            "text_prompt_tokens": 12800,
            "total_tokens": 14788
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
        "case_count": 40,
        "usage": {
          "input_tokens": 45059,
          "output_tokens": 4693,
          "details": {
            "text_prompt_tokens": 45059,
            "total_tokens": 49752
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
        "case_count": 7,
        "usage": {
          "input_tokens": 7575,
          "output_tokens": 1358,
          "details": {
            "text_prompt_tokens": 7575,
            "total_tokens": 8933
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
          "input_tokens": 17427,
          "output_tokens": 2124,
          "details": {
            "text_prompt_tokens": 17427,
            "total_tokens": 19551
          },
          "status": "available"
        },
        "selected_techniques": [],
        "technique_rationales": {},
        "error_type": null,
        "error_stage": null
      },
      "e2edev_bench_03": {
        "status": "generated",
        "case_count": 14,
        "usage": {
          "input_tokens": 17636,
          "output_tokens": 2339,
          "details": {
            "text_prompt_tokens": 17636,
            "total_tokens": 19975
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
          "input_tokens": 21307,
          "output_tokens": 2629,
          "details": {
            "text_prompt_tokens": 21307,
            "total_tokens": 23936
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
