# Team — Group 11

BITS Pilani WILP · PGAIML · PCAM ZG519 Agentic AI · Assignment-1 (Set-3)  
**Due:** Wednesday, 18 November 2026, 11:59 PM  
**Repo:** https://github.com/bits-pgaiml-aai/pcam-zg519-a1-cloud-advisor

| Name | Workstream | Rubric focus | Marks owned |
|------|------------|--------------|-------------|
| S. Bhagat Singh | Classical agents (1–3) + scenario world | Five classical agents (shared) | ~3 of 5 |
| Karthik K | Utility + Learning agents + learning eval | Classical (rest) + Learning & evaluation | ~2 of 5 + 3 |
| Snehalatha M | LLM agent + mock tools + Ollama/LangChain | LLM agent and tool calling | 4 |
| Venkata Srinivasa Rao Tunuguntla | Streamlit UI, integration, docs, screenshots | Shared testing + UI + Documentation | 3 + 3 + 2 |

See [`docs/WORK_SPLIT.md`](docs/WORK_SPLIT.md) for tasks, files, and handoff checklist.

## Shared contracts

- Topic: Cloud Resource and Cost Optimization Advisor
- Scenarios: A (critical), B (cost), C (peak/off-peak), D (edge/ambiguous)
- Classical agents: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based, Learning
- LLM: local Ollama (default `qwen2.5:1.5b-instruct`) via LangChain tool calling
- Tools: `get_resource_metrics`, `get_cost_estimate`, `get_service_level_targets`, `get_scaling_policy`
- UI: Streamlit (`app.py`)
- All six agents must receive the **same** scenario percept for fair comparison
