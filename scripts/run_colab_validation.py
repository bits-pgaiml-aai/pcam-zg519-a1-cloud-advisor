import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.agents.learning import LearningAgent
from src.runner import run_all_agents, simulate_learning_feedback
from src.tools.cloud_tools import (
    get_cost_estimate,
    get_resource_metrics,
    get_scaling_policy,
    get_service_level_targets,
)
from src.world import CloudWorld

world = CloudWorld()
WEIGHTS = {"cost": 0.4, "performance": 0.4, "availability": 0.2}
RUNS = {}
rows = []
for sid in "ABCD":
    payload = run_all_agents(sid, include_llm=False, utility_weights=WEIGHTS)
    RUNS[sid] = payload
    for row in payload["comparison"]:
        rows.append(
            {
                "scenario": sid,
                "agent": row["agent"],
                "recommendation": row["recommendation"],
            }
        )

pivot = pd.DataFrame(rows).pivot(
    index="agent", columns="scenario", values="recommendation"
)
print(pivot)

REQUIRED = [
    "agent",
    "recommendation",
    "reasoning",
    "current_state_summary",
    "trade_offs",
    "monitoring_plan",
]
CLASSICAL = [
    "Simple Reflex",
    "Model-Based Reflex",
    "Goal-Based",
    "Utility-Based",
    "Learning",
]
failures = []


def recs(sid: str) -> dict:
    return {r["agent"]: r["recommendation"] for r in RUNS[sid]["comparison"]}


for sid, payload in RUNS.items():
    agents = []
    for result in payload["results"]:
        agents.append(result["agent"])
        for field in REQUIRED:
            if field not in result or result[field] in (None, ""):
                failures.append(f"{sid}/{result.get('agent')}: missing {field}")
    for name in CLASSICAL:
        if name not in agents:
            failures.append(f"{sid}: missing {name}")

a = recs("A")
for name in CLASSICAL:
    if a.get(name) != "scale_up":
        failures.append(f"A/{name}: {a.get(name)}")

b = recs("B")
for name in ["Simple Reflex", "Model-Based Reflex", "Utility-Based", "Learning"]:
    if b.get(name) != "scale_down":
        failures.append(f"B/{name}: {b.get(name)}")

c = recs("C")
for name in ["Simple Reflex", "Model-Based Reflex"]:
    if c.get(name) != "enable_autoscaling":
        failures.append(f"C/{name}: {c.get(name)}")

metrics = get_resource_metrics("B")
cost = get_cost_estimate(metrics["metrics"]["instance_type"])
sla = get_service_level_targets()
policy = get_scaling_policy("C")
assert "metrics" in metrics
assert "hourly_usd" in cost
assert "sla_targets" in sla
assert "recommended_policy" in policy

llm_payload = run_all_agents(
    "A",
    include_llm=True,
    utility_weights=WEIGHTS,
    llm_model="qwen3:latest",
    llm_host="http://localhost:11434",
)
llm = [r for r in llm_payload["results"] if str(r["agent"]).startswith("LLM")][0]
tools = [t["tool"] for t in (llm.get("tool_trace") or [])]
assert len(tools) >= 2

learner = LearningAgent(explore=0.0, seed=0)
before = deepcopy(learner.history["action_stats"]["scale_up"])
simulate_learning_feedback(learner, "A", "scale_up", True, "nb")
assert learner.history["action_stats"]["scale_up"]["success"] == before["success"] + 1

if failures:
    raise SystemExit(failures)

print("LLM", llm["agent"], llm["recommendation"], tools)
print("ALL CHECKS PASSED")
