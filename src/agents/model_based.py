from __future__ import annotations

from typing import Any

from .simple_reflex import SimpleReflexAgent


class ModelBasedReflexAgent(SimpleReflexAgent):
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

        sla_p95 = percept["sla"]["p95_response_ms"]
        if m["cpu_util_pct"] >= 80 or m["p95_response_ms"] > sla_p95:
            self.state["breach_streak"] += 1
            self.state["low_util_streak"] = 0
        elif m["cpu_util_pct"] <= 30 and m["hourly_cost_usd"] > percept["sla"]["max_hourly_cost_usd"]:
            self.state["low_util_streak"] += 1
            self.state["breach_streak"] = 0
        else:
            self.state["breach_streak"] = max(0, self.state["breach_streak"] - 1)
            self.state["low_util_streak"] = max(0, self.state["low_util_streak"] - 1)

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        self._update_state(percept)
        m = percept["metrics"]
        avg_cpu = sum(self.state["recent_cpu"]) / len(self.state["recent_cpu"])
        avg_p95 = sum(self.state["recent_p95"]) / len(self.state["recent_p95"])
        peak_gap = m["peak_cpu_util_pct"] - m["offpeak_cpu_util_pct"]

        if self.state["breach_streak"] >= 1 and (avg_cpu >= 75 or avg_p95 > percept["sla"]["p95_response_ms"]):
            action = "scale_up"
            reason = (
                f"State shows breach_streak={self.state['breach_streak']}, "
                f"avg_cpu={avg_cpu:.1f}, avg_p95={avg_p95:.1f}; scale_up."
            )
        elif self.state["low_util_streak"] >= 1:
            action = "scale_down"
            reason = f"State shows sustained low utilization (streak={self.state['low_util_streak']}); scale_down."
        elif peak_gap >= 50 and not m["autoscaling_enabled"]:
            action = "enable_autoscaling"
            reason = f"Internal model of workload swing (peak-offpeak={peak_gap:.1f}) suggests autoscaling."
        elif m["autoscaling_enabled"] and avg_p95 > percept["sla"]["p95_response_ms"]:
            action = "rightsize_compute"
            reason = "Autoscaling already on but latency still above SLA; rightsize compute class."
        else:
            action = "keep_current"
            reason = "Believed state is within tolerance; keep current configuration."

        return self._result(
            recommendation=action,
            reasoning=reason,
            candidates=[action],
            extras={
                "current_state_summary": (
                    f"believed avg_cpu={avg_cpu:.1f}%, avg_p95={avg_p95:.1f}ms, "
                    f"breach_streak={self.state['breach_streak']}"
                ),
                "trade_offs": "Uses short history, but still no explicit multi-goal optimization.",
                "monitoring_plan": "Track breach/low-util streaks over successive windows.",
                "internal_state": dict(self.state),
            },
        )
