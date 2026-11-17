# Scenario results summary

Generated from latest `screenshots/scenario_{A–D}.png` companion JSON files.

## Scenario A: High CPU / slow responses

- **Kind:** critical
- **Description:** CPU utilization is consistently high and response time exceeds target.
- **Metrics:** instance=`m5.large`, cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr, avail=99.2%
- **SLA:** p95≤300ms, avail≥99.5%, max_cost=$0.25/hr
- **Utility weights:** cost=0.4, performance=0.4, availability=0.2
- **Screenshot:** [`../screenshots/scenario_A.png`](../screenshots/scenario_A.png)
- **Results JSON:** [`../screenshots/scenario_A_results.json`](../screenshots/scenario_A_results.json)

| Agent | Recommendation | Display |
| --- | --- | --- |
| Simple Reflex | `scale_up` | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Model-Based Reflex | `scale_up` | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Goal-Based | `scale_up` | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Utility-Based | `scale_up` | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Learning | `scale_up` | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| LLM (Ollama/LangChain) | `scale_up` | SCALE_UP - Upsize to c5.xlarge ($122/mo) |

**Why they differ:** Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). scale_up: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based, Learning, LLM (Ollama/LangChain)

## Scenario B: Over-provisioned expensive instance

- **Kind:** normal
- **Description:** CPU and memory utilization are low, but the instance is expensive.
- **Metrics:** instance=`m5.2xlarge`, cpu=18.0%, mem=22.0%, p95=140.0ms, cost=$0.384/hr, avail=99.9%
- **SLA:** p95≤300ms, avail≥99.5%, max_cost=$0.25/hr
- **Utility weights:** cost=0.4, performance=0.4, availability=0.2
- **Screenshot:** [`../screenshots/scenario_B.png`](../screenshots/scenario_B.png)
- **Results JSON:** [`../screenshots/scenario_B_results.json`](../screenshots/scenario_B_results.json)

| Agent | Recommendation | Display |
| --- | --- | --- |
| Simple Reflex | `scale_down` | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| Model-Based Reflex | `scale_down` | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| Goal-Based | `enable_autoscaling` | ENABLE_AUTOSCALING - Keep m5.2xlarge + autoscaling |
| Utility-Based | `scale_down` | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| Learning | `keep_current` | KEEP_CURRENT - Keep m5.2xlarge |
| LLM (Ollama/LangChain) | `scale_down` | SCALE_DOWN - Downsize to t3.medium ($30/mo) |

**Why they differ:** Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). scale_down: Simple Reflex, Model-Based Reflex, Utility-Based, LLM (Ollama/LangChain) | enable_autoscaling: Goal-Based | keep_current: Learning

## Scenario C: Sharp peak / off-peak variation

- **Kind:** normal
- **Description:** Workload varies sharply during peak and off-peak hours.
- **Metrics:** instance=`m5.xlarge`, cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr, avail=99.6%
- **SLA:** p95≤300ms, avail≥99.5%, max_cost=$0.25/hr
- **Utility weights:** cost=0.4, performance=0.4, availability=0.2
- **Screenshot:** [`../screenshots/scenario_C.png`](../screenshots/scenario_C.png)
- **Results JSON:** [`../screenshots/scenario_C_results.json`](../screenshots/scenario_C_results.json)

| Agent | Recommendation | Display |
| --- | --- | --- |
| Simple Reflex | `enable_autoscaling` | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling |
| Model-Based Reflex | `enable_autoscaling` | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling |
| Goal-Based | `scale_up` | SCALE_UP - Upsize to m5.2xlarge ($276/mo) |
| Utility-Based | `enable_autoscaling` | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling |
| Learning | `keep_current` | KEEP_CURRENT - Keep m5.xlarge |
| LLM (Ollama/LangChain) | `keep_current` | KEEP_CURRENT - Keep m5.xlarge |

**Why they differ:** Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). enable_autoscaling: Simple Reflex, Model-Based Reflex, Utility-Based | scale_up: Goal-Based | keep_current: Learning, LLM (Ollama/LangChain)

## Scenario D: Ambiguous mixed signals

- **Kind:** edge
- **Description:** Latency is slightly high, cost is near budget, and CPU is moderate with intermittent spikes.
- **Metrics:** instance=`c5.xlarge`, cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr, avail=99.4%
- **SLA:** p95≤300ms, avail≥99.5%, max_cost=$0.25/hr
- **Utility weights:** cost=0.4, performance=0.4, availability=0.2
- **Screenshot:** [`../screenshots/scenario_D.png`](../screenshots/scenario_D.png)
- **Results JSON:** [`../screenshots/scenario_D_results.json`](../screenshots/scenario_D_results.json)

| Agent | Recommendation | Display |
| --- | --- | --- |
| Simple Reflex | `scale_up` | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| Model-Based Reflex | `scale_up` | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| Goal-Based | `scale_up` | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| Utility-Based | `scale_up` | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| Learning | `scale_up` | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| LLM (Ollama/LangChain) | `scale_up` | SCALE_UP - Upsize to m5.xlarge ($138/mo) |

**Why they differ:** Agents differ because each uses a different decision mechanism (rules vs state vs goal test vs utility vs learned rates vs LLM+tools). scale_up: Simple Reflex, Model-Based Reflex, Goal-Based, Utility-Based, Learning, LLM (Ollama/LangChain)
