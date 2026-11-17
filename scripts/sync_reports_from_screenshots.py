from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SHOTS = ROOT / "screenshots"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
SCENARIOS = ("A", "B", "C", "D")


def _load_submission_helpers():
    path = Path(__file__).with_name("generate_submission_artifacts.py")
    spec = importlib.util.spec_from_file_location("generate_submission_artifacts", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_scenario(sid: str) -> dict:
    path = SHOTS / f"scenario_{sid}_results.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def sync_evidence_json(payloads: dict[str, dict]) -> list[Path]:
    written: list[Path] = []
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for sid, payload in payloads.items():
        dest = EVIDENCE / f"scenario_{sid}_results.json"
        shutil.copy2(SHOTS / f"scenario_{sid}_results.json", dest)
        written.append(dest)
    return written


def write_comparison_summary(payloads: dict[str, dict]) -> Path:
    rows: list[dict] = []
    for sid, payload in payloads.items():
        for row in payload.get("comparison") or []:
            rows.append(
                {
                    "scenario": sid,
                    "agent": row["agent"],
                    "recommendation": row["recommendation"],
                    "display": row.get("display"),
                }
            )
    out = EVIDENCE / "comparison_summary.json"
    out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return out


def write_comparison_csv(payloads: dict[str, dict]) -> Path:
    lines = [
        "scenario,agent,recommendation,display_recommendation,model,tools_called"
    ]
    for sid, payload in payloads.items():
        for result in payload.get("results") or []:
            tools = "|".join(result.get("tools_called") or [])
            lines.append(
                ",".join(
                    [
                        sid,
                        '"' + str(result.get("agent", "")).replace('"', '""') + '"',
                        str(result.get("recommendation", "")),
                        '"'
                        + str(result.get("display_recommendation", "")).replace('"', '""')
                        + '"',
                        str(result.get("model") or ""),
                        '"' + tools + '"',
                    ]
                )
            )
    out = EVIDENCE / "comparison_summary.csv"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_rubric_coverage(payloads: dict[str, dict]) -> Path:
    llm_rows = []
    for sid, payload in payloads.items():
        llm = next(
            (
                r
                for r in payload.get("results") or []
                if str(r.get("agent", "")).startswith("LLM")
            ),
            {},
        )
        tools = ", ".join(llm.get("tools_called") or [])
        llm_rows.append(
            f"| {sid} | `{llm.get('model', '—')}` | {tools or '—'} | `{llm.get('recommendation', '—')}` |"
        )

    lines = [
        "# Rubric coverage checklist",
        "",
        "Mapped to Assignment-1 criteria using the latest `screenshots/scenario_*` evidence.",
        "",
        "| Criterion | Marks | Evidence in this repo |",
        "| --- | ---: | --- |",
        "| Five classical agents | 5 | `src/agents/*.py` — Simple Reflex, Model-Based, Goal-Based, Utility-Based, Learning |",
        "| LLM agent + tool calling | 4 | `src/llm_agent.py`, `src/tools/cloud_tools.py`, `evidence/llm_live_summary.md` |",
        "| Shared scenarios + testing | 3 | Scenarios A–D in `src/world.py`; results in `screenshots/scenario_*_results.json` |",
        "| Streamlit UI + comparison | 3 | `app.py`; full-UI PNGs with Controls pane in `screenshots/scenario_*.png` |",
        "| Learning + evaluation | 3 | `src/agents/learning.py`, `data/learning_history.json`, `docs/learning_before_after.md` |",
        "| Documentation | 2 | `README.md`, `docs/comparison_table.md`, `docs/comparison_writeup.md`, `docs/scenario_results_summary.md` |",
        "",
        "## Required deliverables",
        "",
        "- [x] Source for 5 classical + 1 LLM agent",
        "- [x] `requirements.txt`, README, Streamlit UI, setup/run docs",
        "- [x] ≥3 scenario screenshots + test results (A–D provided)",
        "- [x] Comparison table + why decisions differ",
        "- [x] Learning before/after evidence",
        "- [x] LLM ≥2 tools with live model evidence",
        "",
        "## Latest LLM proof snapshot",
        "",
        "| Scenario | Model | Tools | Recommendation |",
        "| --- | --- | --- | --- |",
        *llm_rows,
        "",
        "Primary comparison docs: [`comparison_table.md`](comparison_table.md), "
        "[`comparison_writeup.md`](comparison_writeup.md), "
        "[`scenario_results_summary.md`](scenario_results_summary.md).",
        "",
        "No video is required for this assignment.",
        "",
    ]
    out = DOCS / "rubric_coverage.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def _agent_map(payload: dict) -> dict[str, dict]:
    return {r["agent"]: r for r in payload.get("results") or []}


def write_comparison_table(payloads: dict[str, dict]) -> Path:
    lines = [
        "# Comparison table — all agents × scenarios",
        "",
        "Built from latest `screenshots/scenario_*_results.json` (same percept per scenario).",
        "",
        "## Recommendation codes",
        "",
        "| Scenario | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning | LLM |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for sid in SCENARIOS:
        agents = _agent_map(payloads[sid])
        llm = next((a for name, a in agents.items() if name.startswith("LLM")), {})
        lines.append(
            "| {sid} | {sr} | {mb} | {gb} | {ub} | {ln} | {llm} |".format(
                sid=sid,
                sr=agents.get("Simple Reflex", {}).get("recommendation", "—"),
                mb=agents.get("Model-Based Reflex", {}).get("recommendation", "—"),
                gb=agents.get("Goal-Based", {}).get("recommendation", "—"),
                ub=agents.get("Utility-Based", {}).get("recommendation", "—"),
                ln=agents.get("Learning", {}).get("recommendation", "—"),
                llm=llm.get("recommendation", "—"),
            )
        )

    lines.extend(
        [
            "",
            "## Display recommendations (UI text)",
            "",
            "| Scenario | Simple Reflex | Model-Based | Goal-Based | Utility-Based | Learning | LLM |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for sid in SCENARIOS:
        agents = _agent_map(payloads[sid])
        llm = next((a for name, a in agents.items() if name.startswith("LLM")), {})
        lines.append(
            "| {sid} | {sr} | {mb} | {gb} | {ub} | {ln} | {llm} |".format(
                sid=sid,
                sr=agents.get("Simple Reflex", {}).get("display_recommendation", "—"),
                mb=agents.get("Model-Based Reflex", {}).get("display_recommendation", "—"),
                gb=agents.get("Goal-Based", {}).get("display_recommendation", "—"),
                ub=agents.get("Utility-Based", {}).get("display_recommendation", "—"),
                ln=agents.get("Learning", {}).get("display_recommendation", "—"),
                llm=llm.get("display_recommendation", "—"),
            )
        )

    lines.extend(
        [
            "",
            "## Why decisions differ",
            "",
            "See [`comparison_writeup.md`](comparison_writeup.md).",
            "",
            "- **Simple Reflex** — threshold rules only.",
            "- **Model-Based Reflex** — short internal streaks / believed state.",
            "- **Goal-Based** — first plan that passes hard goal tests.",
            "- **Utility-Based** — highest scored feasible plan under sidebar weights.",
            "- **Learning** — utility adjusted by success/failure rates in `data/learning_history.json`.",
            "- **LLM** — Ollama/LangChain recommendation grounded in ≥2 tool results.",
            "",
            "Source: [`../evidence/comparison_summary.json`](../evidence/comparison_summary.json) synced from screenshots.",
            "",
        ]
    )
    out = DOCS / "comparison_table.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_comparison_writeup(payloads: dict[str, dict]) -> Path:
    observed_rows = []
    for sid in SCENARIOS:
        payload = payloads[sid]
        scenario = payload.get("scenario") or {}
        agents = _agent_map(payload)
        codes = {name: r.get("recommendation") for name, r in agents.items()}
        unique = sorted({c for c in codes.values() if c})
        observed_rows.append(
            "| {sid} | {name} | `{codes}` | {n} distinct | {why} |".format(
                sid=sid,
                name=scenario.get("name", ""),
                codes=", ".join(
                    f"{k.split('(')[0].strip()}={v}" for k, v in codes.items()
                ),
                n=len(unique),
                why=(payload.get("why_decisions_differ") or "").replace("|", "/"),
            )
        )

    lines = [
        "# Why decisions differ",
        "",
        "All six agents receive the **same** scenario percept (metrics + SLA + catalog). Differences come from mechanism, not from different inputs.",
        "",
        "| Agent | What it optimizes for | Typical weakness |",
        "|-------|----------------------|------------------|",
        "| Simple Reflex | Immediate threshold rules | No memory; may miss sustained trends |",
        "| Model-Based Reflex | Short believed state / streaks | Still no multi-plan search |",
        "| Goal-Based | Any plan that passes hard goals | First feasible plan, not best |",
        "| Utility-Based | Best scored feasible plan | Beliefs are static |",
        "| Learning | Utility adjusted by outcome history | Needs enough feedback; may explore |",
        "| LLM + tools | Natural-language synthesis over tool evidence | Model quality / tool-routing variance |",
        "",
        "## Observed recommendations (latest screenshots)",
        "",
        "| Scenario | Name | Agent codes | Spread | Notes from run |",
        "|----------|------|-------------|--------|----------------|",
        *observed_rows,
        "",
        "## Scenario expectations",
        "",
        "| Scenario | Likely classical lean | Why |",
        "|----------|----------------------|-----|",
        "| A critical high CPU/latency | `scale_up` | Latency and CPU breach dominate |",
        "| B expensive low util | `scale_down` | Cost over budget with spare capacity |",
        "| C peak/off-peak swing | often `enable_autoscaling` | Large peak-offpeak gap; Goal/Learning/LLM may diverge |",
        "| D edge / mixed | often `scale_up` | Mild latency pressure still favors capacity |",
        "",
        "Exact codes above come from `screenshots/scenario_*_results.json`.",
        "",
    ]
    out = DOCS / "comparison_writeup.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_llm_live_summary(payloads: dict[str, dict]) -> Path:
    model = "unknown"
    lines = [
        "# Live LLM tool-calling proof",
        "",
        "Canonical UI evidence from `screenshots/scenario_*_results.json` (synced into `evidence/`).",
        "",
        "| Scenario | Agent label | Model | Tools called | Recommendation | Display |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    detail_blocks: list[str] = []
    for sid in SCENARIOS:
        agents = _agent_map(payloads[sid])
        llm = next((a for name, a in agents.items() if name.startswith("LLM")), None)
        if not llm:
            lines.append(f"| {sid} | — | — | — | — | — |")
            continue
        model = llm.get("model") or model
        tools = ", ".join(llm.get("tools_called") or [])
        lines.append(
            "| {sid} | {agent} | `{model}` | {tools} | `{rec}` | {disp} |".format(
                sid=sid,
                agent=llm.get("agent"),
                model=llm.get("model"),
                tools=tools or "—",
                rec=llm.get("recommendation"),
                disp=llm.get("display_recommendation") or "—",
            )
        )
        detail_blocks.append(f"### Scenario {sid}")
        detail_blocks.append("")
        detail_blocks.append(f"- Reasoning: {(llm.get('reasoning') or '').strip() or '—'}")
        detail_blocks.append(f"- Tools: `{tools}`")
        for step in llm.get("tool_trace") or []:
            detail_blocks.append(
                f"- `{step.get('tool')}` args=`{json.dumps(step.get('args') or {}, sort_keys=True)}`"
            )
        detail_blocks.append("")

    lines[2] = (
        f"Canonical UI evidence from `screenshots/scenario_*_results.json` "
        f"(synced into `evidence/`), model `{model}`."
    )
    lines.extend(["", "## Tool-call detail", ""] + detail_blocks)
    lines.append(
        "Full traces: each LLM result’s `tool_trace` / `reasoning` in `evidence/scenario_*_results.json`."
    )
    lines.append("")
    out = EVIDENCE / "llm_live_summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_scenario_results_summary(payloads: dict[str, dict]) -> Path:
    lines = [
        "# Scenario results summary",
        "",
        "Generated from latest `screenshots/scenario_{A–D}.png` companion JSON files.",
        "",
    ]
    for sid in SCENARIOS:
        payload = payloads[sid]
        scenario = payload.get("scenario") or {}
        metrics = scenario.get("metrics") or {}
        sla = scenario.get("sla") or {}
        weights = payload.get("utility_weights") or {}
        lines.extend(
            [
                f"## Scenario {sid}: {scenario.get('name')}",
                "",
                f"- **Kind:** {scenario.get('kind')}",
                f"- **Description:** {scenario.get('description')}",
                f"- **Metrics:** instance=`{metrics.get('instance_type')}`, "
                f"cpu={metrics.get('cpu_util_pct')}%, mem={metrics.get('memory_util_pct')}%, "
                f"p95={metrics.get('p95_response_ms')}ms, cost=${metrics.get('hourly_cost_usd')}/hr, "
                f"avail={metrics.get('availability_pct')}%",
                f"- **SLA:** p95≤{sla.get('p95_response_ms')}ms, "
                f"avail≥{sla.get('availability_pct')}%, "
                f"max_cost=${sla.get('max_hourly_cost_usd')}/hr",
                f"- **Utility weights:** cost={weights.get('cost')}, "
                f"performance={weights.get('performance')}, "
                f"availability={weights.get('availability')}",
                f"- **Screenshot:** [`../screenshots/scenario_{sid}.png`](../screenshots/scenario_{sid}.png)",
                f"- **Results JSON:** [`../screenshots/scenario_{sid}_results.json`](../screenshots/scenario_{sid}_results.json)",
                "",
                "| Agent | Recommendation | Display |",
                "| --- | --- | --- |",
            ]
        )
        for result in payload.get("results") or []:
            lines.append(
                "| {agent} | `{rec}` | {disp} |".format(
                    agent=result.get("agent"),
                    rec=result.get("recommendation"),
                    disp=result.get("display_recommendation") or "—",
                )
            )
        lines.extend(
            [
                "",
                f"**Why they differ:** {payload.get('why_decisions_differ') or '—'}",
                "",
            ]
        )

    out = DOCS / "scenario_results_summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_rich_screenshots_index(payloads: dict[str, dict]) -> Path:
    lines = [
        "# Screenshots index",
        "",
        "| File | Scenario | Name | LLM model | LLM tools | LLM recommendation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for sid in SCENARIOS:
        scenario = payloads[sid].get("scenario") or {}
        llm = next(
            (
                r
                for r in payloads[sid].get("results") or []
                if str(r.get("agent", "")).startswith("LLM")
            ),
            {},
        )
        tools = ", ".join(llm.get("tools_called") or []) or "—"
        lines.append(
            "| `scenario_{sid}.png` + `scenario_{sid}_results.json` | {sid} | {name} | `{model}` | {tools} | `{rec}` |".format(
                sid=sid,
                name=scenario.get("name", ""),
                model=llm.get("model", "—"),
                tools=tools,
                rec=llm.get("recommendation", "—"),
            )
        )
    lines.extend(
        [
            "",
            "Each PNG is a full UI capture including the left **Controls** pane "
            "(scenario select, utility weights, Ollama model/host, Run all agents).",
            "",
            "See also [`../docs/scenario_results_summary.md`](../docs/scenario_results_summary.md), "
            "[`../docs/comparison_table.md`](../docs/comparison_table.md), "
            "[`../docs/rubric_coverage.md`](../docs/rubric_coverage.md), and `evidence/*.json`.",
            "",
        ]
    )
    out = SHOTS / "INDEX.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    helpers = _load_submission_helpers()
    payloads = {sid: load_scenario(sid) for sid in SCENARIOS}
    written: list[Path] = []
    written.extend(sync_evidence_json(payloads))
    written.append(write_comparison_summary(payloads))
    written.append(write_comparison_csv(payloads))
    written.append(write_comparison_table(payloads))
    written.append(write_comparison_writeup(payloads))
    written.append(write_llm_live_summary(payloads))
    written.append(write_scenario_results_summary(payloads))
    written.append(write_rubric_coverage(payloads))
    written.append(write_rich_screenshots_index(payloads))
    written.append(helpers.write_learning_before_after())
    written.append(helpers.write_submission_pack())
    for path in written:
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
