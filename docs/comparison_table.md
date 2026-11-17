# Comparison table — all agents × scenarios

Same percept for every agent within a scenario. Differences come from mechanism.

| Scenario | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning | LLM |
| --- | --- | --- | --- | --- | --- | --- |
| A | scale_up | scale_up | scale_up | scale_up | scale_up | scale_up |
| B | scale_down | scale_down | enable_autoscaling | scale_down | keep_current | scale_down |
| C | enable_autoscaling | enable_autoscaling | scale_up | enable_autoscaling | keep_current | keep_current |
| D | scale_up | scale_up | scale_up | scale_up | scale_up | scale_up |

## Why decisions differ

See [`comparison_writeup.md`](comparison_writeup.md). Short version:

- **Simple Reflex** — threshold rules only.
- **Model-Based Reflex** — short internal streaks / believed state.
- **Goal-Based** — first plan that passes hard goal tests.
- **Utility-Based** — highest scored feasible plan under sidebar weights.
- **Learning** — utility adjusted by success/failure rates in `data/learning_history.json`.
- **LLM** — Ollama/LangChain recommendation grounded in ≥2 tool results.

Source JSON: [`../evidence/comparison_summary.json`](../evidence/comparison_summary.json).
