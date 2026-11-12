# Team — Group 11

BITS Pilani WILP · PGAIML · PCAM ZG519 Agentic AI · Assignment-1 (Set-3)  
**Due:** Wednesday, 18 November 2026, 11:59 PM  
**Repo:** https://github.com/bits-pgaiml-aai/pcam-zg519-a1-cloud-advisor

## Working model (decided in team discussion)

Each member implements the **full assignment independently**.  
We then compare all four versions against the rubric and **submit the strongest one** as the group submission.

| Name | Implementation folder / branch | Status |
|------|--------------------------------|--------|
| S. Bhagat Singh | `members/bhagat/` or branch `member/bhagat` | In progress |
| Karthik K | `members/karthik/` or branch `member/karthik` | In progress |
| Snehalatha M | `members/snehalatha/` or branch `member/snehalatha` | In progress |
| Venkata Srinivasa Rao Tunuguntla | `members/venkat/` or branch `member/venkat` | In progress |

Shared reference scaffold remains at repo root (starter only). Final submission will replace/promote the winning implementation.

See [`docs/WORK_SPLIT.md`](docs/WORK_SPLIT.md) for rules, rubric checklist, and selection process.

## Shared contracts (every implementation must include)

- Topic: Cloud Resource and Cost Optimization Advisor
- Scenarios: A (critical), B (cost), C (peak/off-peak), plus edge/ambiguous (D or equivalent)
- Five classical agents: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based, Learning
- One LLM agent: local Ollama + LangChain tool calling (≥2 tools, evidence used)
- Streamlit UI with shared-scenario comparison
- Learning agent updates experience / success-failure history
- README, requirements.txt, screenshots, test results
