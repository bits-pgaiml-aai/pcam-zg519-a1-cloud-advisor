# Scenario B — full agent decisions (recovered)

**Scenario:** Over-provisioned expensive instance — CPU and memory utilization are low, but the instance is expensive.

| agent | display |
| --- | --- |
| Simple Reflex | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| Model-Based Reflex | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| Goal-Based | ENABLE_AUTOSCALING - Keep m5.2xlarge + autoscaling |
| Utility-Based | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| Learning | SCALE_DOWN - Downsize to t3.medium ($30/mo) |
| LLM (tool-evidence fallback) | SCALE_DOWN - Downsize to t3.medium ($30/mo) |

## Simple Reflex: SCALE_DOWN - Downsize to t3.medium ($30/mo)

- **recommendation:** `scale_down`
- **current state:** Over-provisioned expensive instance: instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms, cost=$0.384/hr, autoscaling=False (cost>budget)
- **reasoning:** Simple reflex: IF cpu<=25 AND cost>0.25 THEN scale_down. Observed cpu=18.0%, p95=140.0ms, cost=$0.384/hr, gap=20.0.
- **trade-offs:** Fast and deterministic, but ignores history, multi-objective scoring, and candidate instance catalog.
- **monitoring:** Re-evaluate the same threshold rules next window.

## Model-Based Reflex: SCALE_DOWN - Downsize to t3.medium ($30/mo)

- **recommendation:** `scale_down`
- **current state:** Over-provisioned expensive instance: instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms, cost=$0.384/hr, autoscaling=False (cost>budget)
- **reasoning:** Model-based reflex used internal state: sustained low util streak=1.
- **trade-offs:** Uses short memory of unseen trend, but still no explicit goal search or utility ranking.
- **monitoring:** Track breach/low-util streaks across evaluation windows.

## Goal-Based: ENABLE_AUTOSCALING - Keep m5.2xlarge + autoscaling

- **recommendation:** `enable_autoscaling`
- **current state:** Over-provisioned expensive instance: instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms, cost=$0.384/hr, autoscaling=False (cost>budget)
- **reasoning:** Looked ahead over 5 actions; 4 pass the goal test. Took first passing plan (enable_autoscaling). Checks: scale_up:fail, enable_autoscaling:pass, rightsize_compute:pass, scale_down:pass, keep_current:pass.
- **trade-offs:** All passing plans treated as equally good (no utility ranking).
- **monitoring:** Verify predicted p95/cost after the change window.

## Utility-Based: SCALE_DOWN - Downsize to t3.medium ($30/mo)

- **recommendation:** `scale_down`
- **current state:** Over-provisioned expensive instance: instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms, cost=$0.384/hr, autoscaling=False (cost>budget)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [scale_down=-17.28, enable_autoscaling=-27.64, rightsize_compute=-34.56, keep_current=-38.40].
- **trade-offs:** Balances latency penalty, availability gap, and hourly cost; uses advertised/static beliefs only.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## Learning: SCALE_DOWN - Downsize to t3.medium ($30/mo)

- **recommendation:** `scale_down`
- **current state:** Over-provisioned expensive instance: instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms, cost=$0.384/hr, autoscaling=False (cost>budget)
- **reasoning:** Maximized expected utility among feasible plans. Ranking: [scale_down=-13.95, enable_autoscaling=-27.64, rightsize_compute=-34.56, keep_current=-38.40]. Experience-adjusted success rates: scale_down=0.67, enable_autoscaling=0.50, rightsize_compute=0.50, keep_current=0.50.
- **trade-offs:** Improves with outcomes, but needs enough episodes and occasional exploration.
- **monitoring:** Compare realized utility vs predicted after one billing day.

## LLM (tool-evidence fallback): SCALE_DOWN - Downsize to t3.medium ($30/mo)

- **recommendation:** `scale_down`
- **current state:** Over-provisioned expensive instance: instance=m5.2xlarge, cpu=18.0%, mem=22.0%, p95=140.0ms, cost=$0.384/hr, autoscaling=False (cost>budget)
- **reasoning:** Ollama/LangChain unavailable; used deterministic tool evidence fallback. Errors: langchain=No module named 'langchain_core'; ollama=No module named 'ollama'. Recommendation=scale_down from tools ['get_resource_metrics', 'get_cost_estimate'].
- **trade-offs:** Grounded in tool evidence; simulation only; model may mis-rank soft trade-offs.
- **monitoring:** Track p95 latency, CPU, and hourly cost for 24h after any change.
