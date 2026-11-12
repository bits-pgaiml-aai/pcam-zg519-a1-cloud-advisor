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

## Scenario expectations (Venkat implementation)

| Scenario | Likely classical lean | Why |
|----------|----------------------|-----|
| A critical high CPU/latency | `scale_up` | Latency and CPU breach dominate |
| B expensive low util | `scale_down` | Cost over budget with spare capacity |
| C peak/off-peak swing | `enable_autoscaling` | Large peak-offpeak gap |
| D edge / mixed | Split across agents | Mild latency + cost + autoscaling already on |

Exact recommendations can still diverge on D (and sometimes C) between Goal-Based (first pass) and Utility/Learning (ranked / experience-adjusted).
