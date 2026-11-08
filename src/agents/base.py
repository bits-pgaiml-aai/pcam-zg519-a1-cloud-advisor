from __future__ import annotations

from typing import Any


class BaseAgent:
    name = "base"

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def observe(self, outcome: dict[str, Any] | None = None) -> None:
        return None

    def _result(
        self,
        recommendation: str,
        reasoning: str,
        candidates: list[str] | None = None,
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "agent": self.name,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "candidates": candidates or [],
            "current_state_summary": "",
            "trade_offs": "",
            "monitoring_plan": "",
        }
        if extras:
            payload.update(extras)
        return payload
