# Scenario C — full agent decisions (recovered)

**Scenario:** Sharp peak / off-peak variation — Workload varies sharply during peak and off-peak hours.

| agent | display |
| --- | --- |
| Simple Reflex | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling |
| Model-Based Reflex | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling |
| Goal-Based | SCALE_UP - Upsize to m5.2xlarge ($276/mo) |
| Utility-Based | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling |
| Learning | ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling |
| LLM (tool-evidence fallback) | KEEP_CURRENT - Keep m5.xlarge |

## Simple Reflex: ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling

- **recommendation:** `enable_autoscaling`
- **current state:** Sharp peak / off-peak variation: instance=m5.xlarge, cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr, autoscaling=False (no hard SLA breach)
- **reasoning:** Simple reflex: IF peak-offpeak gap>=50 THEN enable_autoscaling. Observed cpu=55.0%, p95=280.0ms, cost=$0.192/hr, gap=79.0.
- **trade-offs:** Fast and deterministic, but ignores history, multi-objective scoring, and candidate instance catalog.
- **monitoring:** Re-evaluate the same threshold rules next window.

## Model-Based Reflex: ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling

- **recommendation:** `enable_autoscaling`
- **current state:** Sharp peak / off-peak variation: instance=m5.xlarge, cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr, autoscaling=False (no hard SLA breach)
- **reasoning:** Model-based reflex used internal state: modelled workload swing peak-offpeak=79.0.
- **trade-offs:** Uses short memory of unseen trend, but still no explicit goal search or utility ranking.
- **monitoring:** Track breach/low-util streaks across evaluation windows.

## Goal-Based: SCALE_UP - Upsize to m5.2xlarge ($276/mo)

- **recommendation:** `scale_up`
- **current state:** Sharp peak / off-peak variation: instance=m5.xlarge, cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr, autoscaling=False (no hard SLA breach)
- **reasoning:** Looked ahead over 5 actions; 4 pass the goal test. Took first passing plan (scale_up). Checks: scale_up:pass, enable_autoscaling:pass, rightsize_compute:pass, scale_down:fail, keep_current:pass.
- **trade-offs:** All passing plans treated as equally good (no utility ranking).
- **monitoring:** Verify predicted p95/cost after the change window.

## Utility-Based: ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling

- **recommendation:** `enable_autoscaling`
- **current state:** Sharp peak / off-peak variation: instance=m5.xlarge, cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr, autoscaling=False (no hard SLA breach)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [enable_autoscaling=-11.32, rightsize_compute=-17.28, keep_current=-19.20, scale_up=-34.56].
- **trade-offs:** Balances latency penalty, availability gap, and hourly cost; uses advertised/static beliefs only.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## Learning: ENABLE_AUTOSCALING - Keep m5.xlarge + autoscaling

- **recommendation:** `enable_autoscaling`
- **current state:** Sharp peak / off-peak variation: instance=m5.xlarge, cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr, autoscaling=False (no hard SLA breach)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [enable_autoscaling=-11.32, rightsize_compute=-17.28, keep_current=-19.20, scale_up=-31.23]. Experience-adjusted success rates: enable_autoscaling=0.50, rightsize_compute=0.50, keep_current=0.50, scale_up=0.67.
- **trade-offs:** Improves with outcomes, but needs enough episodes and occasional exploration.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## LLM (tool-evidence fallback): KEEP_CURRENT - Keep m5.xlarge

- **recommendation:** `keep_current`
- **current state:** Sharp peak / off-peak variation: instance=m5.xlarge, cpu=55.0%, mem=48.0%, p95=280.0ms, cost=$0.192/hr, autoscaling=False (no hard SLA breach)
- **reasoning:** Ollama/LangChain unavailable; used deterministic tool evidence fallback. Errors: langchain=No module named 'langchain_core'; ollama=No module named 'ollama'. Recommendation=keep_current from tools ['get_resource_metrics', 'get_cost_estimate'].
- **trade-offs:** Grounded in tool evidence; simulation only; model may mis-rank soft trade-offs.
- **monitoring:** Track p95 latency, CPU, and hourly cost for 24h after any change.
