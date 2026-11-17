# Live LLM tool-calling proof

Canonical UI evidence from `screenshots/scenario_*_results.json` (synced into `evidence/`), model `qwen3:1.7b`.

| Scenario | Agent label | Model | Tools called | Recommendation | Display |
| --- | --- | --- | --- | --- | --- |
| A | LLM (Ollama/LangChain) | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_up` | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| B | LLM (Ollama/LangChain) | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_down` | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| C | LLM (Ollama/LangChain) | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `keep_current` | KEEP_CURRENT - Keep m5.xlarge |
| D | LLM (Ollama/LangChain) | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_up` | SCALE_UP - Upsize to m5.xlarge ($138/mo) |

## Tool-call detail

### Scenario A

- Reasoning: Normalized recommendation from tool evidence: scale_up.
- Tools: `get_resource_metrics, get_cost_estimate`
- `get_resource_metrics` args=`{"scenario_id": "A"}`
- `get_cost_estimate` args=`{"instance_type": "t2.medium"}`

### Scenario B

- Reasoning: Normalized recommendation from tool evidence: scale_down.
- Tools: `get_resource_metrics, get_cost_estimate`
- `get_resource_metrics` args=`{"scenario_id": "B"}`
- `get_cost_estimate` args=`{"instance_type": "default"}`

### Scenario C

- Reasoning: Normalized recommendation from tool evidence: keep_current.
- Tools: `get_resource_metrics, get_cost_estimate`
- `get_resource_metrics` args=`{"scenario_id": "C"}`
- `get_cost_estimate` args=`{"instance_type": "t2.large"}`

### Scenario D

- Reasoning: Normalized recommendation from tool evidence: scale_up.
- Tools: `get_resource_metrics, get_cost_estimate`
- `get_resource_metrics` args=`{"scenario_id": "D"}`
- `get_cost_estimate` args=`{"instance_type": "t2.medium"}`

Full traces: each LLM result’s `tool_trace` / `reasoning` in `evidence/scenario_*_results.json`.
