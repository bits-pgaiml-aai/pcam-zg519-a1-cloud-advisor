from __future__ import annotations

from typing import Any

from .simple_reflex import SimpleReflexAgent


class ModelBasedReflexAgent(SimpleReflexAgent):
    """Keeps short internal state about recent metrics and breach/low-util streaks."""

    name = "Model-Based Reflex"

    def __init__(self) -> None:
        self.state: dict[str, Any] = {
            "recent_cpu": [],
            "recent_p95": [],
            "recent_cost": [],
            "breach_streak": 0,
            "low_util_streak": 0,
        }

    def _update_state(self, percept: dict[str, Any]) -> None:
        m = percept["metrics"]
        self.state["recent_cpu"].append(m["cpu_util_pct"])
        self.state["recent_p95"].append(m["p95_response_ms"])
        self.state["recent_cost"].append(m["hourly_cost_usd"])
        for key in ("recent_cpu", "recent_p95", "recent_cost"):
            self.state[key] = self.state[key][-5:]

        sla = percept["sla"]
        if m["cpu_util_pct"] >= 80 or m["p95_response_ms"] > sla["p95_response_ms"]:
            self.state["breach_streak"] += 1
            self.state["low_util_streak"] = 0
        elif (
            m["cpu_util_pct"] <= 30
            and m["hourly_cost_usd"] > sla["max_hourly_cost_usd"]
        ):
            self.state["low_util_streak"] += 1
            self.state["breach_streak"] = 0
        else:
            self.state["breach_streak"] = max(0, self.state["breach_streak"] - 1)
            self.state["low_util_streak"] = max(0, self.state["low_util_streak"] - 1)

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        self._update_state(percept)
        m = percept["metrics"]
        sla = percept["sla"]
        avg_cpu = sum(self.state["recent_cpu"]) / len(self.state["recent_cpu"])
        avg_p95 = sum(self.state["recent_p95"]) / len(self.state["recent_p95"])
        peak_gap = m["peak_cpu_util_pct"] - m["offpeak_cpu_util_pct"]
        series_cpu = (percept.get("timeseries") or {}).get("cpu_pct") or []
        prior_cpu = series_cpu[-6:-1] if len(series_cpu) >= 2 else self.state["recent_cpu"][:-1]
        transient_spike = (
            len(prior_cpu) >= 1
            and all(c < 50 for c in prior_cpu)
            and m["cpu_util_pct"] >= 80
        )

        if m["memory_util_pct"] < 0:
            action = "keep_current"
            why = (
                f"missing memory sensor (mem={m['memory_util_pct']}); "
                f"hold sizing until telemetry recovers"
                + ("; recent CPU looks like a single-point spike" if transient_spike else "")
            )
        elif self.state["breach_streak"] >= 1 and (
            avg_cpu >= 75 or avg_p95 > sla["p95_response_ms"]
        ):
            action = "scale_up"
            why = (
                f"believed breach_streak={self.state['breach_streak']}, "
                f"avg_cpu={avg_cpu:.1f}, avg_p95={avg_p95:.1f}"
            )
        elif self.state["low_util_streak"] >= 1:
            action = "scale_down"
            why = f"sustained low util streak={self.state['low_util_streak']}"
        elif peak_gap >= 50 and not m["autoscaling_enabled"]:
            action = "enable_autoscaling"
            why = f"modelled workload swing peak-offpeak={peak_gap:.1f}"
        elif m["autoscaling_enabled"] and avg_p95 > sla["p95_response_ms"]:
            action = "rightsize_compute"
            why = "autoscaling on but believed latency still above SLA"
        else:
            action = "keep_current"
            why = "believed state within tolerance"

        return self._result(
            percept,
            recommendation=action,
            reasoning=f"Model-based reflex used internal state: {why}.",
            candidates=[action],
            trade_offs=(
                "Handles missing sensors and transient spikes via internal state, "
                "but still no explicit goal search or utility ranking."
            ),
            monitoring_plan=(
                "Repair memory telemetry first if missing; otherwise track "
                "breach/low-util streaks across evaluation windows."
            ),
            extras={"internal_state": dict(self.state)},
        )
