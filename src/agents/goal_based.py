from __future__ import annotations

from typing import Any

from .model_based import ModelBasedReflexAgent


class GoalBasedAgent(ModelBasedReflexAgent):
    name = "Goal-Based"

    def _goal_test(self, percept: dict[str, Any], action: str) -> tuple[bool, dict[str, Any]]:
        m = percept["metrics"]
        sla = percept["sla"]
        predicted = {
            "p95_response_ms": m["p95_response_ms"],
            "availability_pct": m["availability_pct"],
            "hourly_cost_usd": m["hourly_cost_usd"],
            "autoscaling_enabled": m["autoscaling_enabled"],
        }

        if action == "scale_up":
            predicted["p95_response_ms"] *= 0.65
            predicted["availability_pct"] = min(99.99, predicted["availability_pct"] + 0.2)
            predicted["hourly_cost_usd"] *= 1.8
        elif action == "scale_down":
            predicted["p95_response_ms"] *= 1.25
            predicted["hourly_cost_usd"] *= 0.45
            predicted["availability_pct"] = max(98.0, predicted["availability_pct"] - 0.1)
        elif action == "enable_autoscaling":
            predicted["p95_response_ms"] = (
                0.4 * m["peak_cpu_util_pct"] + 0.6 * m["offpeak_cpu_util_pct"]
            ) * (m["p95_response_ms"] / max(m["cpu_util_pct"], 1))
            predicted["p95_response_ms"] = min(predicted["p95_response_ms"], m["p95_response_ms"] * 0.9)
            predicted["hourly_cost_usd"] *= 0.85
            predicted["autoscaling_enabled"] = True
        elif action == "rightsize_compute":
            predicted["p95_response_ms"] *= 0.85
            predicted["hourly_cost_usd"] *= 0.9
        elif action == "keep_current":
            pass

        ok = (
            predicted["p95_response_ms"] <= sla["p95_response_ms"] * 1.05
            and predicted["availability_pct"] >= sla["availability_pct"] - 0.2
            and predicted["hourly_cost_usd"] <= sla["max_hourly_cost_usd"] * 1.6
        )
        return ok, predicted

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        self._update_state(percept)
        actions = [
            "scale_up",
            "enable_autoscaling",
            "rightsize_compute",
            "scale_down",
            "keep_current",
        ]
        passing: list[tuple[str, dict[str, Any]]] = []
        notes = []
        for action in actions:
            ok, predicted = self._goal_test(percept, action)
            notes.append(f"{action}:{'pass' if ok else 'fail'}")
            if ok:
                passing.append((action, predicted))

        if not passing:
            return self._result(
                recommendation="escalate_to_human",
                reasoning="No candidate action satisfies latency, availability, and cost goals together.",
                candidates=[],
                extras={
                    "current_state_summary": percept["description"],
                    "trade_offs": "Goal test is pass/fail only; escalate when all plans fail.",
                    "monitoring_plan": "Collect finer metrics before retrying planning.",
                    "goal_checks": notes,
                },
            )

        chosen, predicted = passing[0]
        return self._result(
            recommendation=chosen,
            reasoning=(
                f"Looked ahead over {len(actions)} actions; {len(passing)} pass the goal test. "
                f"Took first passing plan ({chosen}). Checks: {', '.join(notes)}."
            ),
            candidates=[a for a, _ in passing],
            extras={
                "current_state_summary": percept["description"],
                "trade_offs": "All passing plans are treated as equally good.",
                "monitoring_plan": "Verify predicted p95/cost after change window.",
                "predicted_outcome": predicted,
                "goal_checks": notes,
            },
        )
