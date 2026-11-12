from __future__ import annotations

from typing import Any

from src.world import summarize_state


class BaseAgent:
    name = "base"

    def decide(self, percept: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def observe(self, outcome: dict[str, Any] | None = None) -> None:
        return None

    def _result(
        self,
        percept: dict[str, Any],
        recommendation: str,
        reasoning: str,
        candidates: list[str] | None = None,
        trade_offs: str = "",
        monitoring_plan: str = "",
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "agent": self.name,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "candidates": candidates or [recommendation],
            "current_state_summary": summarize_state(percept),
            "trade_offs": trade_offs,
            "monitoring_plan": monitoring_plan
            or "Monitor p95 latency, CPU, availability, and hourly cost for 24h.",
            "mechanism": self.name,
        }
        if extras:
            payload.update(extras)
        return payload
