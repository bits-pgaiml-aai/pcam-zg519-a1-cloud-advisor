# Live LLM tool-calling proof

Canonical UI evidence from `screenshots/scenario_*_results.json` (synced into `evidence/`), model `qwen3:1.7b`.

| Scenario | Agent label | Tools called | Recommendation |
| --- | --- | --- | --- |
| A | LLM (Ollama/LangChain) | get_resource_metrics, get_cost_estimate | scale_up |
| B | LLM (Ollama/LangChain) | get_resource_metrics, get_cost_estimate | scale_down |
| C | LLM (Ollama/LangChain) | get_resource_metrics, get_cost_estimate | keep_current |
| D | LLM (Ollama/LangChain) | get_resource_metrics, get_cost_estimate | scale_up |

Full traces: each LLM result’s `tool_trace` / `reasoning` in `evidence/scenario_*_results.json`.
