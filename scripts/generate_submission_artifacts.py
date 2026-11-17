from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.learning import LearningAgent
from src.display import format_recommendation
from src.runner import run_all_agents, simulate_learning_feedback
from src.world import CloudWorld

EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
SHOTS = ROOT / "screenshots"


def write_comparison_table() -> Path:
    rows = json.loads((EVIDENCE / "comparison_summary.json").read_text(encoding="utf-8"))
    by_scenario: dict[str, list[dict]] = {}
    for row in rows:
        by_scenario.setdefault(row["scenario"], []).append(row)

    lines = [
        "# Comparison table — all agents × scenarios",
        "",
        "Same percept for every agent within a scenario. Differences come from mechanism.",
        "",
        "| Scenario | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning | LLM |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for sid in ("A", "B", "C", "D"):
        agents = {r["agent"]: r["recommendation"] for r in by_scenario.get(sid, [])}
        lines.append(
            "| {sid} | {sr} | {mb} | {gb} | {ub} | {ln} | {llm} |".format(
                sid=sid,
                sr=agents.get("Simple Reflex", "—"),
                mb=agents.get("Model-Based Reflex", "—"),
                gb=agents.get("Goal-Based", "—"),
                ub=agents.get("Utility-Based", "—"),
                ln=agents.get("Learning", "—"),
                llm=next(
                    (
                        v
                        for k, v in agents.items()
                        if str(k).startswith("LLM")
                    ),
                    "—",
                ),
            )
        )

    lines.extend(
        [
            "",
            "## Why decisions differ",
            "",
            "See [`comparison_writeup.md`](comparison_writeup.md). Short version:",
            "",
            "- **Simple Reflex** — threshold rules only.",
            "- **Model-Based Reflex** — short internal streaks / believed state.",
            "- **Goal-Based** — first plan that passes hard goal tests.",
            "- **Utility-Based** — highest scored feasible plan under sidebar weights.",
            "- **Learning** — utility adjusted by success/failure rates in `data/learning_history.json`.",
            "- **LLM** — Ollama/LangChain recommendation grounded in ≥2 tool results.",
            "",
            "Source JSON: [`../evidence/comparison_summary.json`](../evidence/comparison_summary.json).",
            "",
        ]
    )
    out = DOCS / "comparison_table.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_learning_before_after() -> Path:
    tmp_history = EVIDENCE / "_learning_demo_history.json"
    if tmp_history.exists():
        tmp_history.unlink()

    world = CloudWorld()
    percept = world.perceive("D")
    agent = LearningAgent(history_path=tmp_history, explore=0.0, seed=7)

    before = agent.decide(percept)
    before_display = format_recommendation(percept, before["recommendation"])
    before_rates = {
        a: round(agent.success_rate(a), 3) for a in agent.history["action_stats"]
    }

    # Bias against the initial top action and reinforce an alternative.
    initial = before["recommendation"]
    alt = "rightsize_compute" if initial != "rightsize_compute" else "enable_autoscaling"
    simulate_learning_feedback(
        agent, "D", initial, False, "demo: mark initial plan as failure"
    )
    for _ in range(4):
        simulate_learning_feedback(
            agent, "D", alt, True, f"demo: reinforce {alt}"
        )

    after = agent.decide(percept)
    after_display = format_recommendation(percept, after["recommendation"])
    after_rates = {
        a: round(agent.success_rate(a), 3) for a in agent.history["action_stats"]
    }

    payload = {
        "scenario_id": "D",
        "scenario_name": percept["scenario_name"],
        "before": {
            "recommendation": before["recommendation"],
            "display": before_display,
            "reasoning": before["reasoning"],
            "success_rates": before_rates,
            "utility_ranking": before.get("utility_ranking"),
        },
        "feedback_applied": [
            {"action": initial, "success": False, "count": 1},
            {"action": alt, "success": True, "count": 4},
        ],
        "after": {
            "recommendation": after["recommendation"],
            "display": after_display,
            "reasoning": after["reasoning"],
            "success_rates": after_rates,
            "utility_ranking": after.get("utility_ranking"),
        },
        "changed": before["recommendation"] != after["recommendation"],
        "limitations": before.get("limitations"),
    }
    json_out = EVIDENCE / "learning_before_after.json"
    json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Learning agent — before / after feedback",
        "",
        "Demonstration that the Learning agent **uses and updates** outcome history.",
        "Uses a disposable history file (does not overwrite production `data/learning_history.json`).",
        "",
        f"**Scenario D:** {percept['scenario_name']}",
        "",
        "## Before feedback",
        "",
        f"- Recommendation: `{before['recommendation']}` — {before_display}",
        f"- Success rates: `{before_rates}`",
        f"- Reasoning: {before['reasoning']}",
        "",
        "## Feedback applied",
        "",
        f"1. Mark `{initial}` as **failure** (1×).",
        f"2. Mark `{alt}` as **success** (4×).",
        "",
        "## After feedback",
        "",
        f"- Recommendation: `{after['recommendation']}` — {after_display}",
        f"- Success rates: `{after_rates}`",
        f"- Reasoning: {after['reasoning']}",
        f"- Changed vs before: **{payload['changed']}**",
        "",
        "## Limitations",
        "",
        payload["limitations"] or "See docs/learning_evaluation.md",
        "",
        f"Machine-readable: [`../evidence/learning_before_after.json`](../evidence/learning_before_after.json).",
        "",
    ]
    md_out = DOCS / "learning_before_after.md"
    md_out.write_text("\n".join(md_lines), encoding="utf-8")
    tmp_history.unlink(missing_ok=True)
    return md_out


def write_screenshots_index() -> Path:
    lines = [
        "# Screenshots index",
        "",
        "| File | Scenario | Notes |",
        "| --- | --- | --- |",
        "| `scenario_A.png` + `scenario_A_results.json` | A | Critical high CPU / latency |",
        "| `scenario_B.png` + `scenario_B_results.json` | B | Expensive low utilization |",
        "| `scenario_C.png` + `scenario_C_results.json` | C | Peak / off-peak swing |",
        "| `scenario_D.png` + `scenario_D_results.json` | D | Edge / ambiguous |",
        "",
        "One full UI PNG and matching results JSON per scenario. Also see `docs/comparison_table.md` and `evidence/*.json`.",
        "",
    ]
    out = SHOTS / "INDEX.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_submission_pack() -> Path:
    lines = [
        "# Submission pack (Group 11)",
        "",
        "**Due:** Wednesday, 18 November 2026, 11:59 PM",
        "",
        "## What the assignment asks for",
        "",
        "- Source code (5 classical + 1 LLM agent)",
        "- `requirements.txt`, README, Streamlit UI, setup/run instructions",
        "- ≥3 scenario test results and screenshots",
        "- Comparison table and explanation of why decisions differ",
        "",
        "No video upload is required.",
        "",
        "## Include in the Moodle zip / repo pointer",
        "",
        "```text",
        "app.py",
        "requirements.txt",
        "README.md",
        "src/                  # agents, tools, llm_agent, world, runner",
        "data/learning_history.json",
        "evidence/             # scenario_*_results.json, comparison_summary.json,",
        "                      # learning_before_after.json",
        "screenshots/          # scenario_*.png + scenario_*_results.json + INDEX.md",
        "docs/comparison_table.md",
        "docs/comparison_writeup.md",
        "docs/scenario_results_summary.md",
        "docs/rubric_coverage.md",
        "docs/learning_evaluation.md",
        "docs/learning_before_after.md",
        "docs/SELECTION_NOTES.md",
        "```",
        "",
        "## Pre-submit checks",
        "",
        "1. Confirm screenshots A–D PNG + JSON are present under `screenshots/`.",
        "2. Run `python scripts/sync_reports_from_screenshots.py` so evidence/docs match those JSON files.",
        "3. Confirm LLM rows are live Ollama/LangChain with ≥2 tools (see `evidence/llm_live_summary.md`).",
        "4. Fill bake-off winner in `docs/SELECTION_NOTES.md`.",
        "5. Do not include secrets, `.venv/`, or personal PATs.",
        "",
        "## Regenerate helper artifacts",
        "",
        "```bash",
        "python scripts/sync_reports_from_screenshots.py",
        "# optional live re-run (needs Ollama), then sync again:",
        "python scripts/generate_evidence.py",
        "python scripts/sync_reports_from_screenshots.py",
        "```",
        "",
    ]
    out = DOCS / "SUBMISSION_PACK.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    if not (EVIDENCE / "comparison_summary.json").exists():
        raise SystemExit("Run scripts/generate_evidence.py first")

    paths = [
        write_comparison_table(),
        write_learning_before_after(),
        write_screenshots_index(),
        write_submission_pack(),
    ]
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
