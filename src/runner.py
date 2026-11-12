from __future__ import annotations

from typing import Any

from src.agents import CLASSICAL_AGENTS, LearningAgent
from src.llm_agent import run_llm_agent
from src.world import CloudWorld


def run_all_agents(
    scenario_id: str,
    include_llm: bool = True,
    learning_agent: LearningAgent | None = None,
) -> dict[str, Any]:
    world = CloudWorld()
    percept = world.perceive(scenario_id)
    results = []

    for name, cls in CLASSICAL_AGENTS.items():
        agent = learning_agent if name == "Learning" and learning_agent else cls()
        results.append(agent.decide(percept))

    if include_llm:
        results.append(run_llm_agent(scenario_id))

    comparison = [
        {
            "agent": r.get("agent"),
            "recommendation": r.get("recommendation"),
            "reasoning": r.get("reasoning"),
        }
        for r in results
    ]

    why_differ = _explain_differences(comparison)

    return {
        "scenario": {
            "id": percept["scenario_id"],
            "name": percept["scenario_name"],
            "kind": percept["scenario_kind"],
            "description": percept["description"],
            "metrics": percept["metrics"],
            "sla": percept["sla"],
            "candidates": percept["candidates"],
        },
        "results": results,
        "comparison": comparison,
        "why_decisions_differ": why_differ,
    }


def _explain_differences(comparison: list[dict[str, Any]]) -> str:
    by_rec: dict[str, list[str]] = {}
    for row in comparison:
        by_rec.setdefault(row["recommendation"], []).append(row["agent"])
    parts = [f"{rec}: {', '.join(agents)}" for rec, agents in by_rec.items()]
    return (
        "Agents differ because each uses a different decision mechanism "
        "(rules vs state vs goal test vs utility vs learned rates vs LLM+tools). "
        + " | ".join(parts)
    )


def simulate_learning_feedback(
    learning_agent: LearningAgent,
    scenario_id: str,
    action: str,
    success: bool,
    notes: str = "",
) -> dict[str, Any]:
    return learning_agent.learn_from_outcome(scenario_id, action, success, notes)
