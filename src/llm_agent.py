from __future__ import annotations

import json
import os
from typing import Any

from src.tools.cloud_tools import TOOL_FUNCTIONS
from src.world import summarize_state, CloudWorld

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:latest")

SYSTEM_PROMPT = """
You are a Cloud Resource and Cost Optimization Advisor.
Use tools to gather evidence before recommending an action.
You must call at least two relevant tools.
Recommend one of: keep_current, scale_up, scale_down, enable_autoscaling, rightsize_compute.
If memory telemetry is missing, prefer keep_current until sensors recover.
Explain trade-offs. Do not claim you changed any cloud resources.
Ground the recommendation in tool evidence.
""".strip()

ADVISORY_SYSTEM_PROMPT = """
You are a senior Cloud Resource and Cost Optimization Advisor.
Write a clear plain-English advisory report grounded ONLY in the provided tool evidence.
Do NOT output JSON or tool-call tags. Do NOT claim you changed cloud resources.
Use these exact 5 markdown headings:
### 1. Current-State Summary
### 2. Candidate Configurations
### 3. Estimated Cost/Performance Trade-offs
### 4. Recommendation
### 5. Monitoring Plan
In section 4, name exactly one action from:
keep_current, scale_up, scale_down, enable_autoscaling, rightsize_compute.
""".strip()

OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_resource_metrics",
            "description": "Get simulated CPU/memory/latency/cost metrics for scenario A/B/C/D.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario_id": {
                        "type": "string",
                        "description": "Scenario id such as A, B, C, or D",
                    }
                },
                "required": ["scenario_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_cost_estimate",
            "description": "Estimate hourly/monthly cost for an instance type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instance_type": {"type": "string"},
                    "hours_per_month": {"type": "integer"},
                },
                "required": ["instance_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_service_level_targets",
            "description": "Get latency, availability, and cost SLA targets.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scaling_policy",
            "description": "Get a suggested autoscaling policy for the scenario.",
            "parameters": {
                "type": "object",
                "properties": {"scenario_id": {"type": "string"}},
                "required": ["scenario_id"],
            },
        },
    },
]


def _run_tool(name: str, arguments: dict[str, Any]) -> Any:
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    return fn(**arguments)


def _extract_recommendation(text: str) -> str:
    in_rec = False
    for line in (text or "").splitlines():
        clean = line.strip().lstrip("#*- ").strip()
        lower = clean.lower()
        if "4. recommendation" in lower:
            in_rec = True
            continue
        if in_rec and clean and not lower.startswith("5."):
            for action in (
                "enable_autoscaling",
                "rightsize_compute",
                "scale_up",
                "scale_down",
                "keep_current",
                "escalate_to_human",
            ):
                if action in lower:
                    return action
            break

    lowered = (text or "").lower()
    for action in (
        "enable_autoscaling",
        "rightsize_compute",
        "scale_up",
        "scale_down",
        "keep_current",
        "escalate_to_human",
    ):
        if action in lowered:
            return action
    return "keep_current"


def _recommendation_summary(text: str, recommendation: str) -> str:
    in_rec = False
    for line in (text or "").splitlines():
        clean = line.strip().lstrip("#*- ").strip()
        lower = clean.lower()
        if "4. recommendation" in lower:
            in_rec = True
            continue
        if in_rec and clean and not lower.startswith("5."):
            return clean[:120]
    return recommendation


def _evidence_block(tool_trace: list[dict[str, Any]]) -> str:
    lines = []
    for item in tool_trace:
        lines.append(f"- {item['tool']}(): {json.dumps(item.get('result'), default=str)}")
    return "\n".join(lines)


def _heuristic_from_tools(scenario_id: str, tool_trace: list[dict[str, Any]]) -> str:
    metrics = None
    sla = None
    policy = None
    for item in tool_trace:
        result = item.get("result") or {}
        if item["tool"] == "get_resource_metrics":
            metrics = result.get("metrics")
        elif item["tool"] == "get_service_level_targets":
            sla = (result.get("sla_targets") or {})
        elif item["tool"] == "get_scaling_policy":
            policy = result.get("recommended_policy")
    if not metrics:
        metrics = CloudWorld().get_scenario(scenario_id)["metrics"]
    if not sla:
        sla = CloudWorld().perceive(scenario_id)["sla"]
    if metrics.get("memory_util_pct", 0) < 0:
        return "keep_current"
    if metrics["p95_response_ms"] > sla["p95_response_ms"] or metrics["cpu_util_pct"] >= 85:
        return "scale_up"
    if metrics["cpu_util_pct"] <= 25 and metrics["hourly_cost_usd"] > sla["max_hourly_cost_usd"]:
        return "scale_down"
    if policy and policy.get("prefer_autoscaling"):
        return "enable_autoscaling"
    if metrics["autoscaling_enabled"] and metrics["p95_response_ms"] > sla["p95_response_ms"]:
        return "rightsize_compute"
    return "keep_current"


def _ensure_min_tools(scenario_id: str, tool_trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    used = {item["tool"] for item in tool_trace}
    if "get_resource_metrics" not in used:
        args = {"scenario_id": scenario_id}
        tool_trace.append(
            {"tool": "get_resource_metrics", "args": args, "result": _run_tool("get_resource_metrics", args)}
        )
    if "get_service_level_targets" not in used and "get_cost_estimate" not in used:
        metrics = next(
            (t["result"]["metrics"] for t in tool_trace if t["tool"] == "get_resource_metrics"),
            CloudWorld().get_scenario(scenario_id)["metrics"],
        )
        args = {"instance_type": metrics["instance_type"]}
        tool_trace.append(
            {"tool": "get_cost_estimate", "args": args, "result": _run_tool("get_cost_estimate", args)}
        )
    if len(tool_trace) < 2:
        tool_trace.append(
            {
                "tool": "get_service_level_targets",
                "args": {},
                "result": _run_tool("get_service_level_targets", {}),
            }
        )
    return tool_trace


def _package(
    scenario_id: str,
    recommendation: str,
    reasoning: str,
    tool_trace: list[dict[str, Any]],
    model_name: str,
    agent_label: str,
    full_report: str | None = None,
) -> dict[str, Any]:
    percept = CloudWorld().perceive(scenario_id)
    report = (full_report or reasoning or "").strip()
    return {
        "agent": agent_label,
        "recommendation": recommendation,
        "display_recommendation": _recommendation_summary(report, recommendation),
        "reasoning": (
            f"Called {len(tool_trace)} tools: "
            f"{', '.join(t['tool'] for t in tool_trace)}."
        ),
        "full_report": report,
        "tool_trace": tool_trace,
        "candidates": [recommendation],
        "current_state_summary": summarize_state(percept),
        "trade_offs": (
            "Synthesizes multi-tool evidence into natural-language trade-offs "
            "and a monitoring plan; simulation only."
        ),
        "monitoring_plan": "Track p95 latency, CPU, memory telemetry health, and hourly cost for 24h.",
        "model": model_name,
        "tools_called": [t["tool"] for t in tool_trace],
    }


def run_llm_agent(scenario_id: str, model: str | None = None) -> dict[str, Any]:
    """LLM agent using local Ollama tool calling through LangChain when available."""
    model_name = model or DEFAULT_MODEL
    scenario_id = scenario_id.upper()
    tool_trace: list[dict[str, Any]] = []

    try:
        return _run_langchain(scenario_id, model_name, tool_trace)
    except Exception as exc:  # noqa: BLE001 - fall back for assignment demos
        try:
            return _run_ollama_native(scenario_id, model_name, tool_trace)
        except Exception as exc2:  # noqa: BLE001
            tool_trace = _ensure_min_tools(scenario_id, [])
            recommendation = _heuristic_from_tools(scenario_id, tool_trace)
            reasoning = (
                "Ollama/LangChain unavailable; used deterministic tool evidence fallback. "
                f"Errors: langchain={exc}; ollama={exc2}. "
                f"Recommendation={recommendation} from tools { [t['tool'] for t in tool_trace] }."
            )
            report = (
                "### 1. Current-State Summary\n"
                f"{CloudWorld().perceive(scenario_id)['description']}\n\n"
                "### 2. Candidate Configurations\n"
                "Derived from catalog via tool evidence.\n\n"
                "### 3. Estimated Cost/Performance Trade-offs\n"
                "Ollama unavailable; used deterministic tool heuristics.\n\n"
                f"### 4. Recommendation\n{recommendation}\n\n"
                "### 5. Monitoring Plan\n"
                "Track p95 latency, CPU, memory telemetry health, and hourly cost for 24h."
            )
            return _package(
                scenario_id,
                recommendation,
                reasoning,
                tool_trace,
                model_name,
                "LLM (tool-evidence fallback)",
                full_report=report,
            )


def _run_langchain(
    scenario_id: str, model_name: str, tool_trace: list[dict[str, Any]]
) -> dict[str, Any]:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
    from langchain_ollama import ChatOllama

    base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    base_llm = ChatOllama(model=model_name, temperature=0, base_url=base_url)
    llm = base_llm.bind_tools(
        [
            TOOL_FUNCTIONS["get_resource_metrics"],
            TOOL_FUNCTIONS["get_cost_estimate"],
            TOOL_FUNCTIONS["get_service_level_targets"],
            TOOL_FUNCTIONS["get_scaling_policy"],
        ]
    )
    messages: list[Any] = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Analyze cloud scenario {scenario_id}. "
                "Call at least two tools to gather metrics, cost, SLA, and scaling evidence."
            )
        ),
    ]
    ai: AIMessage = llm.invoke(messages)
    messages.append(ai)

    for call in getattr(ai, "tool_calls", None) or []:
        name = call["name"]
        args = call.get("args") or {}
        result = _run_tool(name, args)
        tool_trace.append({"tool": name, "args": args, "result": result})
        messages.append(ToolMessage(content=json.dumps(result), tool_call_id=call.get("id", name)))

    if len(tool_trace) < 2:
        extra = llm.invoke(
            messages
            + [HumanMessage(content="Call one more relevant tool before writing the advisory.")]
        )
        messages.append(extra)
        for call in getattr(extra, "tool_calls", []) or []:
            name = call["name"]
            args = call.get("args") or {}
            result = _run_tool(name, args)
            tool_trace.append({"tool": name, "args": args, "result": result})
            messages.append(
                ToolMessage(content=json.dumps(result), tool_call_id=call.get("id", name))
            )

    tool_trace = _ensure_min_tools(scenario_id, tool_trace)
    final = base_llm.invoke(
        [
            SystemMessage(content=ADVISORY_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Scenario: {scenario_id}\n\n"
                    f"Verified Tool Evidence:\n{_evidence_block(tool_trace)}\n\n"
                    "Provide your structured 5-part advisory report now."
                )
            ),
        ]
    )
    text = final.content if isinstance(final.content, str) else str(final.content)
    recommendation = _extract_recommendation(text)
    if recommendation == "keep_current":
        recommendation = _heuristic_from_tools(scenario_id, tool_trace)
    return _package(
        scenario_id,
        recommendation,
        text,
        tool_trace,
        model_name,
        "LLM (Ollama/LangChain)",
        full_report=text,
    )


def _run_ollama_native(
    scenario_id: str, model_name: str, tool_trace: list[dict[str, Any]]
) -> dict[str, Any]:
    import ollama

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Analyze cloud scenario {scenario_id}. "
                "Call at least two tools to gather metrics, cost, SLA, and scaling evidence."
            ),
        },
    ]
    response = ollama.chat(model=model_name, messages=messages, tools=OLLAMA_TOOLS)
    message = response["message"]
    tool_calls = message.get("tool_calls") or []

    if tool_calls:
        messages.append(message)
        for call in tool_calls:
            fn = call.get("function", {})
            name = fn.get("name")
            args = fn.get("arguments") or {}
            if isinstance(args, str):
                args = json.loads(args)
            result = _run_tool(name, args)
            tool_trace.append({"tool": name, "args": args, "result": result})
            messages.append({"role": "tool", "tool_name": name, "content": json.dumps(result)})

    tool_trace = _ensure_min_tools(scenario_id, tool_trace)
    final = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": ADVISORY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Scenario: {scenario_id}\n\n"
                    f"Verified Tool Evidence:\n{_evidence_block(tool_trace)}\n\n"
                    "Provide your structured 5-part advisory report now."
                ),
            },
        ],
    )
    text = final["message"]["content"]

    recommendation = _extract_recommendation(text)
    if recommendation == "keep_current":
        recommendation = _heuristic_from_tools(scenario_id, tool_trace)
    return _package(
        scenario_id,
        recommendation,
        text,
        tool_trace,
        model_name,
        "LLM (Ollama)",
        full_report=text,
    )
