from __future__ import annotations

from typing import Any

from src.world import INSTANCE_CATALOG, estimate_monthly_cost


ACTION_TITLES = {
    "keep_current": "KEEP_CURRENT",
    "scale_up": "SCALE_UP",
    "scale_down": "SCALE_DOWN",
    "enable_autoscaling": "ENABLE_AUTOSCALING",
    "rightsize_compute": "RIGHTSIZE_COMPUTE",
    "escalate_to_human": "ESCALATE",
}


def pick_target_instance(percept: dict[str, Any], action: str) -> str | None:
    current = percept["metrics"]["instance_type"]
    current_cost = INSTANCE_CATALOG[current]["hourly_usd"]
    catalog = sorted(INSTANCE_CATALOG.items(), key=lambda item: item[1]["hourly_usd"])

    if action == "keep_current":
        return current
    if action == "scale_down":
        cheaper = [name for name, spec in catalog if spec["hourly_usd"] < current_cost]
        return cheaper[0] if cheaper else current
    if action == "scale_up":
        dearer = [name for name, spec in catalog if spec["hourly_usd"] > current_cost]
        return dearer[0] if dearer else current
    if action == "rightsize_compute":
        mids = [
            name
            for name, spec in catalog
            if abs(spec["hourly_usd"] - current_cost) > 1e-9
        ]
        return mids[len(mids) // 2] if mids else current
    if action == "enable_autoscaling":
        return current
    return None


def format_recommendation(percept: dict[str, Any], action: str) -> str:
    title = ACTION_TITLES.get(action, action.upper())
    target = pick_target_instance(percept, action)
    if action == "scale_down" and target:
        monthly = estimate_monthly_cost(INSTANCE_CATALOG[target]["hourly_usd"])
        return f"{title} - Downsize to {target} (${monthly:.0f}/mo)"
    if action == "scale_up" and target:
        monthly = estimate_monthly_cost(INSTANCE_CATALOG[target]["hourly_usd"])
        return f"{title} - Upsize to {target} (${monthly:.0f}/mo)"
    if action == "enable_autoscaling":
        return f"{title} - Keep {percept['metrics']['instance_type']} + autoscaling"
    if action == "rightsize_compute" and target:
        return f"{title} - Move toward {target}"
    if action == "keep_current":
        return f"{title} - Keep {percept['metrics']['instance_type']}"
    if action == "escalate_to_human":
        return f"{title} - No safe automated plan"
    return title


def enrich_result(percept: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    action = result.get("recommendation", "keep_current")
    enriched = dict(result)
    enriched["display_recommendation"] = format_recommendation(percept, action)
    enriched["target_instance"] = pick_target_instance(percept, action)
    return enriched
