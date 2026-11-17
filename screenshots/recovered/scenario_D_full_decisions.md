# Scenario D — full agent decisions (recovered)

**Scenario:** Ambiguous mixed signals — Latency is slightly high, cost is near budget, and CPU is moderate with intermittent spikes.

| agent | display |
| --- | --- |
| Simple Reflex | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| Model-Based Reflex | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| Goal-Based | SCALE_UP - Upsize to m5.xlarge ($138/mo) |
| Utility-Based | ENABLE_AUTOSCALING - Keep c5.xlarge + autoscaling |
| Learning | ENABLE_AUTOSCALING - Keep c5.xlarge + autoscaling |
| LLM (tool-evidence fallback) | SCALE_UP - Upsize to m5.xlarge ($138/mo) |

## Simple Reflex: SCALE_UP - Upsize to m5.xlarge ($138/mo)

- **recommendation:** `scale_up`
- **current state:** Ambiguous mixed signals: instance=c5.xlarge, cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr, autoscaling=True (latency>SLA, availability<SLA)
- **reasoning:** Simple reflex: IF cpu>=85 OR p95>300 THEN scale_up. Observed cpu=64.0%, p95=330.0ms, cost=$0.17/hr, gap=49.0.
- **trade-offs:** Fast and deterministic, but ignores history, multi-objective scoring, and candidate instance catalog.
- **monitoring:** Re-evaluate the same threshold rules next window.

## Model-Based Reflex: SCALE_UP - Upsize to m5.xlarge ($138/mo)

- **recommendation:** `scale_up`
- **current state:** Ambiguous mixed signals: instance=c5.xlarge, cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr, autoscaling=True (latency>SLA, availability<SLA)
- **reasoning:** Model-based reflex used internal state: believed breach_streak=1, avg_cpu=64.0, avg_p95=330.0.
- **trade-offs:** Uses short memory of unseen trend, but still no explicit goal search or utility ranking.
- **monitoring:** Track breach/low-util streaks across evaluation windows.

## Goal-Based: SCALE_UP - Upsize to m5.xlarge ($138/mo)

- **recommendation:** `scale_up`
- **current state:** Ambiguous mixed signals: instance=c5.xlarge, cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr, autoscaling=True (latency>SLA, availability<SLA)
- **reasoning:** Looked ahead over 5 actions; 3 pass the goal test. Took first passing plan (scale_up). Checks: scale_up:pass, enable_autoscaling:pass, rightsize_compute:pass, scale_down:fail, keep_current:fail.
- **trade-offs:** All passing plans treated as equally good (no utility ranking).
- **monitoring:** Verify predicted p95/cost after the change window.

## Utility-Based: ENABLE_AUTOSCALING - Keep c5.xlarge + autoscaling

- **recommendation:** `enable_autoscaling`
- **current state:** Ambiguous mixed signals: instance=c5.xlarge, cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr, autoscaling=True (latency>SLA, availability<SLA)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [enable_autoscaling=-14.45, rightsize_compute=-20.30, scale_up=-30.60].
- **trade-offs:** Balances latency penalty, availability gap, and hourly cost; uses advertised/static beliefs only.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## Learning: ENABLE_AUTOSCALING - Keep c5.xlarge + autoscaling

- **recommendation:** `enable_autoscaling`
- **current state:** Ambiguous mixed signals: instance=c5.xlarge, cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr, autoscaling=True (latency>SLA, availability<SLA)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [enable_autoscaling=-14.45, rightsize_compute=-20.30, scale_up=-27.27]. Experience-adjusted success rates: enable_autoscaling=0.50, rightsize_compute=0.50, scale_up=0.67.
- **trade-offs:** Improves with outcomes, but needs enough episodes and occasional exploration.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## LLM (tool-evidence fallback): SCALE_UP - Upsize to m5.xlarge ($138/mo)

- **recommendation:** `scale_up`
- **current state:** Ambiguous mixed signals: instance=c5.xlarge, cpu=64.0%, mem=71.0%, p95=330.0ms, cost=$0.17/hr, autoscaling=True (latency>SLA, availability<SLA)
- **reasoning:** Ollama/LangChain unavailable; used deterministic tool evidence fallback. Errors: langchain=No module named 'langchain_core'; ollama=No module named 'ollama'. Recommendation=scale_up from tools ['get_resource_metrics', 'get_cost_estimate'].
- **trade-offs:** Grounded in tool evidence; simulation only; model may mis-rank soft trade-offs.
- **monitoring:** Track p95 latency, CPU, and hourly cost for 24h after any change.
