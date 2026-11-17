# Scenario A — full agent decisions (recovered)

**Scenario:** High CPU / slow responses — CPU utilization is consistently high and response time exceeds target.

| agent | display |
| --- | --- |
| Simple Reflex | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Model-Based Reflex | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Goal-Based | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Utility-Based | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| Learning | SCALE_UP - Upsize to c5.xlarge ($122/mo) |
| LLM (tool-evidence fallback) | SCALE_UP - Upsize to c5.xlarge ($122/mo) |

## Simple Reflex: SCALE_UP - Upsize to c5.xlarge ($122/mo)

- **recommendation:** `scale_up`
- **current state:** High CPU / slow responses: instance=m5.large, cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr, autoscaling=False (latency>SLA, availability<SLA)
- **reasoning:** Simple reflex: IF cpu>=85 OR p95>300 THEN scale_up. Observed cpu=92.0%, p95=520.0ms, cost=$0.096/hr, gap=8.0.
- **trade-offs:** Fast and deterministic, but ignores history, multi-objective scoring, and candidate instance catalog.
- **monitoring:** Re-evaluate the same threshold rules next window.

## Model-Based Reflex: SCALE_UP - Upsize to c5.xlarge ($122/mo)

- **recommendation:** `scale_up`
- **current state:** High CPU / slow responses: instance=m5.large, cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr, autoscaling=False (latency>SLA, availability<SLA)
- **reasoning:** Model-based reflex used internal state: believed breach_streak=1, avg_cpu=92.0, avg_p95=520.0.
- **trade-offs:** Uses short memory of unseen trend, but still no explicit goal search or utility ranking.
- **monitoring:** Track breach/low-util streaks across evaluation windows.

## Goal-Based: SCALE_UP - Upsize to c5.xlarge ($122/mo)

- **recommendation:** `scale_up`
- **current state:** High CPU / slow responses: instance=m5.large, cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr, autoscaling=False (latency>SLA, availability<SLA)
- **reasoning:** Looked ahead over 5 actions; 1 pass the goal test. Took first passing plan (scale_up). Checks: scale_up:pass, enable_autoscaling:fail, rightsize_compute:fail, scale_down:fail, keep_current:fail.
- **trade-offs:** All passing plans treated as equally good (no utility ranking).
- **monitoring:** Verify predicted p95/cost after the change window.

## Utility-Based: SCALE_UP - Upsize to c5.xlarge ($122/mo)

- **recommendation:** `scale_up`
- **current state:** High CPU / slow responses: instance=m5.large, cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr, autoscaling=False (latency>SLA, availability<SLA)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [scale_up=-17.28].
- **trade-offs:** Balances latency penalty, availability gap, and hourly cost; uses advertised/static beliefs only.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## Learning: SCALE_UP - Upsize to c5.xlarge ($122/mo)

- **recommendation:** `scale_up`
- **current state:** High CPU / slow responses: instance=m5.large, cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr, autoscaling=False (latency>SLA, availability<SLA)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [scale_up=-13.95]. Experience-adjusted success rates: scale_up=0.67.
- **trade-offs:** Improves with outcomes, but needs enough episodes and occasional exploration.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## LLM (tool-evidence fallback): SCALE_UP - Upsize to c5.xlarge ($122/mo)

- **recommendation:** `scale_up`
- **current state:** High CPU / slow responses: instance=m5.large, cpu=92.0%, mem=68.0%, p95=520.0ms, cost=$0.096/hr, autoscaling=False (latency>SLA, availability<SLA)
- **reasoning:** Ollama/LangChain unavailable; used deterministic tool evidence fallback. Errors: langchain=No module named 'langchain_core'; ollama=No module named 'ollama'. Recommendation=scale_up from tools ['get_resource_metrics', 'get_cost_estimate'].
- **trade-offs:** Grounded in tool evidence; simulation only; model may mis-rank soft trade-offs.
- **monitoring:** Track p95 latency, CPU, and hourly cost for 24h after any change.
