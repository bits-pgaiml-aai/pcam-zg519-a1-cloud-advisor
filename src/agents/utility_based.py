from __future__ import annotations

from typing import Any

from .goal_based import GoalBasedAgent


class UtilityBasedAgent(GoalBasedAgent):
    """Scores feasible plans and picks the highest expected utility."""

    name = "Utility-Based"

    def __init__(
        self,
        cost_weight: float = 0.4,
        performance_weight: float = 0.4,
        availability_weight: float = 0.2,
    ) -> None:
        super().__init__()
        total = max(cost_weight + performance_weight + availability_weight, 1e-9)
        self.cost_weight = cost_weight / total
        self.performance_weight = performance_weight / total
        self.availability_weight = availability_weight / total

    def expected_utility(self, percept: dict[str, Any], action: str) -> float:
        ok, predicted = self._goal_test(percept, action)
        if not ok:
            return float("-inf")

        sla = percept["sla"]
        # Higher is better, normalized roughly to [0, 1] components.
        cost_score = max(
            0.0,
            1.0 - predicted["hourly_cost_usd"] / max(sla["max_hourly_cost_usd"] * 2.0, 1e-9),
        )
        perf_score = max(
            0.0,
            1.0
            - max(0.0, predicted["p95_response_ms"] - sla["p95_response_ms"] * 0.5)
            / max(sla["p95_response_ms"], 1e-9),
        )
        avail_score = min(1.0, predicted["availability_pct"] / 100.0)
        if predicted["p95_response_ms"] > sla["p95_response_ms"]:
            perf_score *= 0.7
        if predicted["availability_pct"] < sla["availability_pct"]:
            avail_score *= 0.7

        utility = (
            self.cost_weight * cost_score
            + self.performance_weight * perf_score
            + self.availability_weight * avail_score
        )
        if action == "enable_autoscaling":
            utility += 0.02
        return round(utility, 4)

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
        weights = (
            f"cost={self.cost_weight:.2f}, performance={self.performance_weight:.2f}, "
            f"availability={self.availability_weight:.2f}"
        )
        if best_u == float("-inf"):
            return self._result(
                percept,
                recommendation="escalate_to_human",
                reasoning=(
                    "No feasible action under hard constraints; utility undefined. "
                    f"Weights: {weights}."
                ),
                candidates=[],
                trade_offs="Cannot optimize when every plan fails the goal test.",
                monitoring_plan="Relax one constraint or add capacity options.",
                extras={"utility_ranking": [(a, u) for u, a in ranked]},
            )

        shown = ", ".join(
            f"{action}={utility:.3f}" for utility, action in ranked if utility != float("-inf")
        )
        return self._result(
            percept,
            recommendation=best,
            reasoning=(
                f"Highest weighted utility ({best_u:.3f}) using {weights}. "
                f"Ranking: [{shown}]."
            ),
            candidates=[a for u, a in ranked if u != float("-inf")],
            trade_offs=(
                "Sidebar weights change the ranking; SLO breaches reduce performance/"
                "availability scores."
            ),
            monitoring_plan="Compare realized utility vs predicted after one billing day.",
            extras={
                "utility_ranking": [(a, u) for u, a in ranked if u != float("-inf")],
                "utility_weights": {
                    "cost": self.cost_weight,
                    "performance": self.performance_weight,
                    "availability": self.availability_weight,
                },
            },
        )
