from __future__ import annotations

import json
import os
from typing import Any

from src.tools.cloud_tools import TOOL_FUNCTIONS

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b-instruct")

SYSTEM_PROMPT = """
You are a Cloud Resource and Cost Optimization Advisor.
Use tools to gather evidence before recommending an action.
You must call at least two relevant tools.
Recommend one of: keep_current, scale_up, scale_down, enable_autoscaling, rightsize_compute.
Explain trade-offs. Do not claim you changed any cloud resources.
Return a concise recommendation grounded in tool evidence.
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


def run_llm_agent(scenario_id: str, model: str | None = None) -> dict[str, Any]:
    """LLM agent using local Ollama tool calling (LangChain-compatible evidence path)."""
    model_name = model or DEFAULT_MODEL
    tool_trace: list[dict[str, Any]] = []

    try:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
        from langchain_ollama import ChatOllama
    except ImportError:
        return _run_ollama_native(scenario_id, model_name)

    llm = ChatOllama(model=model_name, temperature=0).bind_tools(
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
                "Call at least two tools, then recommend one action with reasoning."
            )
        ),
    ]

    ai: AIMessage = llm.invoke(messages)
    messages.append(ai)

    if not getattr(ai, "tool_calls", None):
        return {
            "agent": "LLM (Ollama/LangChain)",
            "recommendation": "keep_current",
            "reasoning": ai.content or "Model returned no tool calls.",
            "tool_trace": tool_trace,
            "candidates": [],
            "current_state_summary": f"scenario={scenario_id}",
            "trade_offs": "No tool evidence collected.",
            "monitoring_plan": "Re-run with a tool-capable model if needed.",
            "model": model_name,
        }

    for call in ai.tool_calls:
        name = call["name"]
        args = call.get("args") or {}
        result = _run_tool(name, args)
        tool_trace.append({"tool": name, "args": args, "result": result})
        messages.append(
            ToolMessage(content=json.dumps(result), tool_call_id=call.get("id", name))
        )

    if len(tool_trace) < 2:
        extra = llm.invoke(
            messages
            + [
                HumanMessage(
                    content="Call one more relevant tool before final recommendation."
                )
            ]
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

    final = llm.invoke(messages)
    text = final.content if isinstance(final.content, str) else str(final.content)
    recommendation = _extract_recommendation(text)

    return {
        "agent": "LLM (Ollama/LangChain)",
        "recommendation": recommendation,
        "reasoning": text,
        "tool_trace": tool_trace,
        "candidates": [recommendation],
        "current_state_summary": f"scenario={scenario_id}; tools_used={len(tool_trace)}",
        "trade_offs": "Grounded in tool evidence; model may still mis-rank soft trade-offs.",
        "monitoring_plan": "Track p95 latency, CPU, and hourly cost for 24h after any change.",
        "model": model_name,
    }


def _run_ollama_native(scenario_id: str, model_name: str) -> dict[str, Any]:
    import ollama

    tool_trace: list[dict[str, Any]] = []
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Analyze cloud scenario {scenario_id}. "
                "Call at least two tools, then recommend one action."
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
            messages.append(
                {"role": "tool", "tool_name": name, "content": json.dumps(result)}
            )
        if len(tool_trace) < 2:
            metrics = _run_tool("get_resource_metrics", {"scenario_id": scenario_id})
            sla = _run_tool("get_service_level_targets", {})
            tool_trace.extend(
                [
                    {
                        "tool": "get_resource_metrics",
                        "args": {"scenario_id": scenario_id},
                        "result": metrics,
                    },
                    {"tool": "get_service_level_targets", "args": {}, "result": sla},
                ]
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_name": "get_resource_metrics",
                    "content": json.dumps(metrics),
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_name": "get_service_level_targets",
                    "content": json.dumps(sla),
                }
            )
        final = ollama.chat(model=model_name, messages=messages)
        text = final["message"]["content"]
    else:
        metrics = _run_tool("get_resource_metrics", {"scenario_id": scenario_id})
        cost = _run_tool(
            "get_cost_estimate",
            {"instance_type": metrics["metrics"]["instance_type"]},
        )
        tool_trace = [
            {
                "tool": "get_resource_metrics",
                "args": {"scenario_id": scenario_id},
                "result": metrics,
            },
            {
                "tool": "get_cost_estimate",
                "args": {"instance_type": metrics["metrics"]["instance_type"]},
                "result": cost,
            },
        ]
        text = (
            "Model did not emit tool calls; used deterministic tool evidence fallback. "
            f"Metrics={json.dumps(metrics)}; Cost={json.dumps(cost)}"
        )

    recommendation = _extract_recommendation(text)
    return {
        "agent": "LLM (Ollama)",
        "recommendation": recommendation,
        "reasoning": text,
        "tool_trace": tool_trace,
        "candidates": [recommendation],
        "current_state_summary": f"scenario={scenario_id}; tools_used={len(tool_trace)}",
        "trade_offs": "Evidence-grounded; simulation only.",
        "monitoring_plan": "Watch p95, CPU, and cost after any recommended change.",
        "model": model_name,
    }


def _extract_recommendation(text: str) -> str:
    lowered = text.lower()
    for action in (
        "enable_autoscaling",
        "rightsize_compute",
        "scale_up",
        "scale_down",
        "keep_current",
    ):
        if action in lowered:
            return action
    return "keep_current"
