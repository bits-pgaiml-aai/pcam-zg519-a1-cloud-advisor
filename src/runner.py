from __future__ import annotations

import os
from typing import Any

from src.agents import (
    GoalBasedAgent,
    LearningAgent,
    ModelBasedReflexAgent,
    SimpleReflexAgent,
    UtilityBasedAgent,
)
from src.display import enrich_result
from src.llm_agent import run_llm_agent
from src.world import CloudWorld


def run_all_agents(
    scenario_id: str,
    include_llm: bool = True,
    learning_agent: LearningAgent | None = None,
    utility_weights: dict[str, float] | None = None,
    llm_model: str | None = None,
    llm_host: str | None = None,
) -> dict[str, Any]:
    world = CloudWorld()
    percept = world.perceive(scenario_id)
    weights = utility_weights or {
        "cost": 0.4,
        "performance": 0.4,
        "availability": 0.2,
    }

    if learning_agent is None:
        learning_agent = LearningAgent(
            cost_weight=weights["cost"],
            performance_weight=weights["performance"],
            availability_weight=weights["availability"],
        )

    agents = [
        SimpleReflexAgent(),
        ModelBasedReflexAgent(),
        GoalBasedAgent(),
        UtilityBasedAgent(
            cost_weight=weights["cost"],
            performance_weight=weights["performance"],
            availability_weight=weights["availability"],
        ),
        learning_agent,
    ]
    results = [enrich_result(percept, agent.decide(percept)) for agent in agents]

    if include_llm:
        if llm_host:
            os.environ["OLLAMA_HOST"] = llm_host
        results.append(
            enrich_result(percept, run_llm_agent(scenario_id, model=llm_model))
        )

    comparison = [
        {
            "agent": r.get("agent"),
            "recommendation": r.get("recommendation"),
            "display": r.get("display_recommendation"),
            "reasoning": r.get("reasoning"),
        }
        for r in results
    ]

    return {
        "scenario": {
            "id": percept["scenario_id"],
            "name": percept["scenario_name"],
            "kind": percept["scenario_kind"],
            "description": percept["description"],
            "metrics": percept["metrics"],
            "sla": percept["sla"],
            "candidates": percept["candidates"],
            "timeseries": percept["timeseries"],
            "kpis": percept["kpis"],
        },
        "results": results,
        "comparison": comparison,
        "why_decisions_differ": _explain_differences(comparison),
        "utility_weights": weights,
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
