from __future__ import annotations

from typing import Any

from .base import BaseAgent


class SimpleReflexAgent(BaseAgent):
    """Maps current percept to action with fixed condition→action rules. No memory."""

    name = "Simple Reflex"

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        m = percept["metrics"]
        sla = percept["sla"]
        cpu = m["cpu_util_pct"]
        cost = m["hourly_cost_usd"]
        p95 = m["p95_response_ms"]
        peak_gap = m["peak_cpu_util_pct"] - m["offpeak_cpu_util_pct"]

        if cpu >= 85 or p95 > sla["p95_response_ms"]:
            action = "scale_up"
            fired = f"IF cpu>=85 OR p95>{sla['p95_response_ms']} THEN scale_up"
        elif cpu <= 25 and cost > sla["max_hourly_cost_usd"]:
            action = "scale_down"
            fired = (
                f"IF cpu<=25 AND cost>{sla['max_hourly_cost_usd']} THEN scale_down"
            )
        elif peak_gap >= 50:
            action = "enable_autoscaling"
            fired = "IF peak-offpeak gap>=50 THEN enable_autoscaling"
        else:
            action = "keep_current"
            fired = "DEFAULT keep_current (no higher-priority rule fired)"

        return self._result(
            percept,
            recommendation=action,
            reasoning=(
                f"Simple reflex: {fired}. "
                f"Observed cpu={cpu}%, p95={p95}ms, cost=${cost}/hr, gap={peak_gap:.1f}."
            ),
            candidates=[action],
            trade_offs=(
                "Fast and deterministic, but ignores history, multi-objective scoring, "
                "and candidate instance catalog."
            ),
            monitoring_plan="Re-evaluate the same threshold rules next window.",
        )
