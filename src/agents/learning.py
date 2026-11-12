from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from .utility_based import UtilityBasedAgent

DEFAULT_HISTORY_PATH = Path(__file__).resolve().parents[2] / "data" / "learning_history.json"


class LearningAgent(UtilityBasedAgent):
    """Utility performance element + critic/learning element over action outcomes."""

    name = "Learning"

    def __init__(
        self,
        history_path: Path | None = None,
        explore: float = 0.15,
        seed: int = 7,
    ) -> None:
        super().__init__()
        self.history_path = history_path or DEFAULT_HISTORY_PATH
        self.explore = explore
        self.rng = random.Random(seed)
        self.history = self._load_history()

    def _load_history(self) -> dict[str, Any]:
        if self.history_path.exists():
            return json.loads(self.history_path.read_text(encoding="utf-8"))
        return {
            "action_stats": {
                action: {"success": 1, "failure": 1}
                for action in (
                    "keep_current",
                    "scale_up",
                    "scale_down",
                    "enable_autoscaling",
                    "rightsize_compute",
                )
            },
            "episodes": [],
        }

    def _save_history(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(json.dumps(self.history, indent=2), encoding="utf-8")

    def success_rate(self, action: str) -> float:
        stats = self.history["action_stats"].get(action, {"success": 1, "failure": 1})
        total = stats["success"] + stats["failure"]
        return stats["success"] / total

    def expected_utility(self, percept: dict[str, Any], action: str) -> float:
        base = super().expected_utility(percept, action)
        if base == float("-inf"):
            return base
        return base + 20.0 * (self.success_rate(action) - 0.5)

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        decision = super().decide(percept)
        decision["agent"] = self.name
        ranking = decision.get("utility_ranking", [])
        feasible = [a for a, u in ranking if u != float("-inf")]
        rates = ", ".join(f"{a}={self.success_rate(a):.2f}" for a in feasible) or "n/a"

        if len(feasible) > 1 and self.rng.random() < self.explore:
            alt = self.rng.choice(feasible[1:])
            decision["recommendation"] = alt
            decision["reasoning"] = (
                f"Learning agent exploring alternative '{alt}' to gather outcome evidence. "
                f"Experience-adjusted success rates: {rates}."
            )
        else:
            decision["reasoning"] += f" Experience-adjusted success rates: {rates}."

        decision["learning_stats"] = {
            action: {
                "success_rate": round(self.success_rate(action), 3),
                **self.history["action_stats"][action],
            }
            for action in self.history["action_stats"]
        }
        decision["limitations"] = (
            "Early counts are priors; sparse feedback can bias preferences. "
            "Exploration may temporarily pick a suboptimal plan."
        )
        decision["trade_offs"] = (
            "Improves with outcomes, but needs enough episodes and occasional exploration."
        )
        return decision

    def learn_from_outcome(
        self,
        scenario_id: str,
        action: str,
        success: bool,
        notes: str = "",
    ) -> dict[str, Any]:
        stats = self.history["action_stats"].setdefault(action, {"success": 1, "failure": 1})
        if success:
            stats["success"] += 1
        else:
            stats["failure"] += 1
        self.history["episodes"].append(
            {
                "scenario_id": scenario_id,
                "action": action,
                "success": success,
                "notes": notes,
            }
        )
        self._save_history()
        return {
            "updated_action": action,
            "success_rate": round(self.success_rate(action), 3),
            "episodes": len(self.history["episodes"]),
        }
