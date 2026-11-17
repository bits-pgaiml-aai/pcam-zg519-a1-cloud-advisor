# Rubric coverage checklist

Mapped to Assignment-1 criteria using the latest `screenshots/scenario_*` evidence.

| Criterion | Marks | Evidence in this repo |
| --- | ---: | --- |
| Five classical agents | 5 | `src/agents/*.py` — Simple Reflex, Model-Based, Goal-Based, Utility-Based, Learning |
| LLM agent + tool calling | 4 | `src/llm_agent.py`, `src/tools/cloud_tools.py`, `evidence/llm_live_summary.md` |
| Shared scenarios + testing | 3 | Scenarios A–D in `src/world.py`; results in `screenshots/scenario_*_results.json` |
| Streamlit UI + comparison | 3 | `app.py`; full-UI PNGs with Controls pane in `screenshots/scenario_*.png` |
| Learning + evaluation | 3 | `src/agents/learning.py`, `data/learning_history.json`, `docs/learning_before_after.md` |
| Documentation | 2 | `README.md`, `docs/comparison_table.md`, `docs/comparison_writeup.md`, `docs/scenario_results_summary.md` |

## Required deliverables

- [x] Source for 5 classical + 1 LLM agent
- [x] `requirements.txt`, README, Streamlit UI, setup/run docs
- [x] ≥3 scenario screenshots + test results (A–D provided)
- [x] Comparison table + why decisions differ
- [x] Learning before/after evidence
- [x] LLM ≥2 tools with live model evidence

## Latest LLM proof snapshot

| Scenario | Model | Tools | Recommendation |
| --- | --- | --- | --- |
| A | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_up` |
| B | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_down` |
| C | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `keep_current` |
| D | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_up` |

Primary comparison docs: [`comparison_table.md`](comparison_table.md), [`comparison_writeup.md`](comparison_writeup.md), [`scenario_results_summary.md`](scenario_results_summary.md).

No video is required for this assignment.
