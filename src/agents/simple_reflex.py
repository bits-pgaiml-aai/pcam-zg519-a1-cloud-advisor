from __future__ import annotations

from typing import Any

from .base import BaseAgent


class SimpleReflexAgent(BaseAgent):
    name = "Simple Reflex"

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        m = percept["metrics"]
        cpu = m["cpu_util_pct"]
        cost = m["hourly_cost_usd"]
        p95 = m["p95_response_ms"]
        sla_p95 = percept["sla"]["p95_response_ms"]
        budget = percept["sla"]["max_hourly_cost_usd"]

        if cpu >= 85 or p95 > sla_p95:
            action = "scale_up"
            reason = f"Rule: IF cpu>={85} OR p95>{sla_p95} THEN scale_up (cpu={cpu}, p95={p95})."
        elif cpu <= 25 and cost > budget:
            action = "scale_down"
            reason = f"Rule: IF cpu<={25} AND cost>{budget} THEN scale_down (cpu={cpu}, cost={cost})."
        elif abs(m["peak_cpu_util_pct"] - m["offpeak_cpu_util_pct"]) >= 50:
            action = "enable_autoscaling"
            reason = "Rule: IF peak-offpeak gap >= 50 THEN enable_autoscaling."
        else:
            action = "keep_current"
            reason = "Rule: default keep_current when no high-priority condition fires."

        return self._result(
            recommendation=action,
            reasoning=reason,
            candidates=[action],
            extras={
                "current_state_summary": f"cpu={cpu}%, p95={p95}ms, cost=${cost}/hr",
                "trade_offs": "Ignores multi-objective balance; reacts to one condition only.",
                "monitoring_plan": "Re-check the same thresholds next evaluation window.",
            },
        )
