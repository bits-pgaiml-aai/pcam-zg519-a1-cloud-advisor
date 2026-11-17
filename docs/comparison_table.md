# Comparison table — all agents × scenarios

Built from latest `screenshots/scenario_*_results.json` (same percept per scenario).

## Recommendation codes

| Scenario | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning | LLM |
| --- | --- | --- | --- | --- | --- | --- |
| A | scale_up | scale_up | scale_up | scale_up | scale_up | scale_up |
| B | scale_down | scale_down | enable_autoscaling | scale_down | keep_current | scale_down |
| C | enable_autoscaling | enable_autoscaling | scale_up | enable_autoscaling | keep_current | keep_current |
| D | scale_up | scale_up | scale_up | scale_up | scale_up | scale_up |

## Display recommendations (UI text)

| Scenario | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning | LLM |
| --- | --- | --- | --- | --- | --- | --- |
| A | SCALE_UP - Upsize to c5.xlarge ($122/mo) | SCALE_UP - Upsize to c5.xlarge ($122/mo) | SCALE_UP - Upsize to c5.xlarge ($122/mo) | SCALE_UP - Upsize to c5.xlarge ($122/mo) | SCALE_UP - Upsize to c5.xlarge ($122/mo) | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| B | SCALE_DOWN - Downsize to t3.medium ($30/mo) | SCALE_DOWN - Downsize to t3.medium ($30/mo) | ENABLE_AUTOSCALING - Keep m5.2xlarge + autoscaling | SCALE_DOWN - Downsize to t3.medium ($30/mo) | KEEP_CURRENT - Keep m5.2xlarge | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| C | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling | SCALE_UP - Upsize to m5.2xlarge ($276/mo) | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling | KEEP_CURRENT - Keep m5.xlarge | KEEP_CURRENT - Keep m5.xlarge |
| D | SCALE_UP - Upsize to m5.xlarge ($138/mo) | SCALE_UP - Upsize to m5.xlarge ($138/mo) | SCALE_UP - Upsize to m5.xlarge ($138/mo) | SCALE_UP - Upsize to m5.xlarge ($138/mo) | SCALE_UP - Upsize to m5.xlarge ($138/mo) | SCALE_UP - Upsize to m5.xlarge ($138/mo) |

## Why decisions differ

See [`comparison_writeup.md`](comparison_writeup.md).

- **Simple Reflex** — threshold rules only.
- **Model-Based Reflex** — short internal streaks / believed state.
- **Goal-Based** — first plan that passes hard goal tests.
- **Utility-Based** — highest scored feasible plan under sidebar weights.
- **Learning** — utility adjusted by success/failure rates in `data/learning_history.json`.
- **LLM** — Ollama/LangChain recommendation grounded in ≥2 tool results.

Source: [`../evidence/comparison_summary.json`](../evidence/comparison_summary.json) synced from screenshots.
