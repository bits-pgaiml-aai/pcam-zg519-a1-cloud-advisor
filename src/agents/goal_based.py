from __future__ import annotations

from typing import Any

from .model_based import ModelBasedReflexAgent


class GoalBasedAgent(ModelBasedReflexAgent):
    """Looks ahead over candidate actions and keeps only plans that pass the goal test."""

    name = "Goal-Based"

    def _goal_test(
        self, percept: dict[str, Any], action: str
    ) -> tuple[bool, dict[str, Any]]:
        m = percept["metrics"]
        sla = percept["sla"]
        predicted = {
            "p95_response_ms": m["p95_response_ms"],
            "availability_pct": m["availability_pct"],
            "hourly_cost_usd": m["hourly_cost_usd"],
            "autoscaling_enabled": m["autoscaling_enabled"],
        }

        if action == "scale_up":
            predicted["p95_response_ms"] = min(m["p95_response_ms"] * 0.55, sla["p95_response_ms"] * 0.95)
            predicted["availability_pct"] = min(99.99, predicted["availability_pct"] + 0.3)
            predicted["hourly_cost_usd"] *= 1.8
        elif action == "scale_down":
            predicted["p95_response_ms"] *= 1.25
            predicted["hourly_cost_usd"] *= 0.45
            predicted["availability_pct"] = max(98.0, predicted["availability_pct"] - 0.1)
        elif action == "enable_autoscaling":
            blend = 0.35 * m["peak_cpu_util_pct"] + 0.65 * m["offpeak_cpu_util_pct"]
            scale = blend / max(m["cpu_util_pct"], 1.0)
            predicted["p95_response_ms"] = min(
                m["p95_response_ms"] * 0.85, m["p95_response_ms"] * max(scale, 0.55)
            )
            predicted["hourly_cost_usd"] *= 0.85
            predicted["autoscaling_enabled"] = True
        elif action == "rightsize_compute":
            predicted["p95_response_ms"] = min(m["p95_response_ms"] * 0.8, sla["p95_response_ms"] * 1.02)
            predicted["hourly_cost_usd"] *= 0.9
        elif action == "keep_current":
            pass

        ok = (
            predicted["p95_response_ms"] <= sla["p95_response_ms"] * 1.08
            and predicted["availability_pct"] >= sla["availability_pct"] - 0.25
            and predicted["hourly_cost_usd"] <= sla["max_hourly_cost_usd"] * 1.8
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
                percept,
                recommendation="escalate_to_human",
                reasoning=(
                    "Goal-based look-ahead found 0 feasible plans under latency, "
                    f"availability, and cost goals. Checks: {', '.join(notes)}."
                ),
                candidates=[],
                trade_offs="Escalate rather than pick an unsafe plan.",
                monitoring_plan="Collect finer metrics before retrying planning.",
                extras={"goal_checks": notes},
            )

        chosen, predicted = passing[0]
        return self._result(
            percept,
            recommendation=chosen,
            reasoning=(
                f"Looked ahead over {len(actions)} actions; {len(passing)} pass the "
                f"goal test. Took first passing plan ({chosen}). Checks: "
                f"{', '.join(notes)}."
            ),
            candidates=[a for a, _ in passing],
            trade_offs="All passing plans treated as equally good (no utility ranking).",
            monitoring_plan="Verify predicted p95/cost after the change window.",
            extras={"predicted_outcome": predicted, "goal_checks": notes},
        )
