from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.learning import LearningAgent
from src.runner import run_all_agents, simulate_learning_feedback

EVIDENCE = ROOT / "evidence"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    learner = LearningAgent()
    simulate_learning_feedback(learner, "A", "scale_up", True, "seed success for scale_up")
    simulate_learning_feedback(learner, "B", "scale_down", True, "seed success for scale_down")

    summary_rows = []
    for scenario_id in ("A", "B", "C", "D"):
        payload = run_all_agents(
            scenario_id, include_llm=True, learning_agent=learner
        )
        out = EVIDENCE / f"scenario_{scenario_id}_results.json"
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        for row in payload["comparison"]:
            summary_rows.append(
                {
                    "scenario": scenario_id,
                    "agent": row["agent"],
                    "recommendation": row["recommendation"],
                }
            )
        print(f"wrote {out}")

    table = EVIDENCE / "comparison_summary.json"
    table.write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    print(f"wrote {table}")


if __name__ == "__main__":
    main()
