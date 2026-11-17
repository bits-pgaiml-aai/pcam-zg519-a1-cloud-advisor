# Why decisions differ

All six agents receive the **same** scenario percept (metrics + SLA + catalog). Differences come from mechanism, not from different inputs.

| Agent | What it optimizes for | Typical weakness |
|-------|----------------------|------------------|
| Simple Reflex | Immediate threshold rules | No memory; may miss sustained trends |
| Model-Based Reflex | Short believed state / streaks | Still no multi-plan search |
| Goal-Based | Any plan that passes hard goals | First feasible plan, not best |
| Utility-Based | Best scored feasible plan | Beliefs are static |
| Learning | Utility adjusted by outcome history | Needs enough feedback; may explore |
| LLM + tools | Natural-language synthesis over tool evidence | Model quality / tool-routing variance |

## Observed recommendations (latest screenshots)

| Scenario | Name | Agent codes | Spread | Notes from run |
|----------|------|-------------|--------|----------------|
| A | High CPU / slow responses | `Simple Reflex=scale_up, Model-Based Reflex=scale_up, Goal-Based=scale_up, Utility-Based=scale_up, Learning=scale_up, LLM=scale_up` | 1 distinct | Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). scale_up: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based, Learning, LLM (Ollama/LangChain) |
| B | Over-provisioned expensive instance | `Simple Reflex=scale_down, Model-Based Reflex=scale_down, Goal-Based=enable_autoscaling, Utility-Based=scale_down, Learning=keep_current, LLM=scale_down` | 3 distinct | Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). scale_down: Simple Reflex, Model-Based Reflex, Utility-Based, LLM (Ollama/LangChain) / enable_autoscaling: Goal-Based / keep_current: Learning |
| C | Sharp peak / off-peak variation | `Simple Reflex=enable_autoscaling, Model-Based Reflex=enable_autoscaling, Goal-Based=scale_up, Utility-Based=enable_autoscaling, Learning=keep_current, LLM=keep_current` | 3 distinct | Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). enable_autoscaling: Simple Reflex, Model-Based Reflex, Utility-Based / scale_up: Goal-Based / keep_current: Learning, LLM (Ollama/LangChain) |
| D | Ambiguous mixed signals | `Simple Reflex=scale_up, Model-Based Reflex=scale_up, Goal-Based=scale_up, Utility-Based=scale_up, Learning=scale_up, LLM=scale_up` | 1 distinct | Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). scale_up: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based, Learning, LLM (Ollama/LangChain) |

## Scenario expectations

| Scenario | Likely classical lean | Why |
|----------|----------------------|-----|
| A critical high CPU/latency | `scale_up` | Latency and CPU breach dominate |
| B expensive low util | `scale_down` | Cost over budget with spare capacity |
| C peak/off-peak swing | often `enable_autoscaling` | Large peak-offpeak gap; Goal/Learning/LLM may diverge |
| D edge / mixed | often `scale_up` | Mild latency pressure still favors capacity |

Exact codes above come from `screenshots/scenario_*_results.json`.
