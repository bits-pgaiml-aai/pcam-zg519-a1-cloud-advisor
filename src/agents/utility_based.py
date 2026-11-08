from __future__ import annotations

from typing import Any

from .goal_based import GoalBasedAgent


class UtilityBasedAgent(GoalBasedAgent):
    name = "Utility-Based"

    def expected_utility(self, percept: dict[str, Any], action: str) -> float:
        ok, predicted = self._goal_test(percept, action)
        if not ok:
            return float("-inf")

        sla = percept["sla"]
        latency_penalty = max(0.0, predicted["p95_response_ms"] - sla["p95_response_ms"]) / 10.0
        availability_gap = max(0.0, sla["availability_pct"] - predicted["availability_pct"]) * 50.0
        cost_term = predicted["hourly_cost_usd"] * 100.0
        stability_bonus = 5.0 if action == "enable_autoscaling" else 0.0
        return -(latency_penalty + availability_gap + cost_term) + stability_bonus

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        self._update_state(percept)
        actions = [
            "scale_up",
            "enable_autoscaling",
            "rightsize_compute",
            "scale_down",
            "keep_current",
        ]
        ranked = sorted(
            ((self.expected_utility(percept, action), action) for action in actions),
            key=lambda item: item[0],
            reverse=True,
        )
        best_u, best = ranked[0]
        if best_u == float("-inf"):
            return self._result(
                recommendation="escalate_to_human",
                reasoning="No feasible action under hard constraints; cannot score utility.",
                candidates=[],
                extras={
                    "current_state_summary": percept["description"],
                    "trade_offs": "Utility undefined when all plans fail constraints.",
                    "monitoring_plan": "Relax one constraint or gather more capacity options.",
                    "utility_ranking": [(a, u) for u, a in ranked],
                },
            )

        shown = ", ".join(
            f"{action}={utility:.2f}" for utility, action in ranked if utility != float("-inf")
        )
        return self._result(
            recommendation=best,
            reasoning=f"Maximized expected utility among feasible plans. Ranking: [{shown}].",
            candidates=[a for u, a in ranked if u != float("-inf")],
            extras={
                "current_state_summary": percept["description"],
                "trade_offs": "Balances latency penalty, availability gap, and hourly cost.",
                "monitoring_plan": "Compare realized utility vs predicted after one billing day.",
                "utility_ranking": [(a, u) for u, a in ranked if u != float("-inf")],
            },
        )
