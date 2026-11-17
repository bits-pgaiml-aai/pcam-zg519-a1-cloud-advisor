# Screenshots index

| File | Scenario | Name | LLM model | LLM tools | LLM recommendation |
| --- | --- | --- | --- | --- | --- |
| `scenario_A.png` + `scenario_A_results.json` | A | High CPU / slow responses | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_up` |
| `scenario_B.png` + `scenario_B_results.json` | B | Over-provisioned expensive instance | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_down` |
| `scenario_C.png` + `scenario_C_results.json` | C | Sharp peak / off-peak variation | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `keep_current` |
| `scenario_D.png` + `scenario_D_results.json` | D | Ambiguous mixed signals | `qwen3:1.7b` | get_resource_metrics, get_cost_estimate | `scale_up` |

One full UI PNG and matching results JSON per scenario.
See also [`../docs/scenario_results_summary.md`](../docs/scenario_results_summary.md), [`../docs/comparison_table.md`](../docs/comparison_table.md), and `evidence/*.json`.
