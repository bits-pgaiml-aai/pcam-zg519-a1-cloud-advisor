from __future__ import annotations

from typing import Any

from src.world import INSTANCE_CATALOG, SLA_TARGETS, CloudWorld

_world = CloudWorld()


def get_resource_metrics(scenario_id: str) -> dict[str, Any]:
    """Return simulated cloud workload metrics for a scenario (A/B/C/D)."""
    scenario = _world.get_scenario(scenario_id.upper())
    return {
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "kind": scenario["kind"],
        "description": scenario["description"],
        "metrics": scenario["metrics"],
    }


def get_cost_estimate(instance_type: str, hours_per_month: int = 720) -> dict[str, Any]:
    """Estimate hourly and monthly cost for an instance type from the local catalog."""
    if instance_type not in INSTANCE_CATALOG:
        return {
            "error": f"Unknown instance_type '{instance_type}'",
            "known_types": sorted(INSTANCE_CATALOG),
        }
    hourly = INSTANCE_CATALOG[instance_type]["hourly_usd"]
    cheaper = sorted(
        (
            {
                "instance_type": name,
                "hourly_usd": spec["hourly_usd"],
                "monthly_usd": round(spec["hourly_usd"] * hours_per_month, 2),
            }
            for name, spec in INSTANCE_CATALOG.items()
            if spec["hourly_usd"] < hourly
        ),
        key=lambda row: row["hourly_usd"],
    )
    return {
        "instance_type": instance_type,
        "hourly_usd": hourly,
        "monthly_usd": round(hourly * hours_per_month, 2),
        "hours_per_month": hours_per_month,
        "spec": INSTANCE_CATALOG[instance_type],
        "cheaper_alternatives": cheaper[:3],
    }


def get_service_level_targets() -> dict[str, Any]:
    """Return service-level targets used by the advisor (latency, availability, cost)."""
    return {"sla_targets": dict(SLA_TARGETS)}


def get_scaling_policy(scenario_id: str) -> dict[str, Any]:
    """Return a suggested scaling policy for the selected scenario."""
    scenario = _world.get_scenario(scenario_id.upper())
    m = scenario["metrics"]
    peak_gap = m["peak_cpu_util_pct"] - m["offpeak_cpu_util_pct"]
    return {
        "scenario_id": scenario["id"],
        "current_autoscaling_enabled": m["autoscaling_enabled"],
        "peak_offpeak_cpu_gap": peak_gap,
        "recommended_policy": {
            "scale_out_cpu_threshold_pct": 70,
            "scale_in_cpu_threshold_pct": 30,
            "cooldown_seconds": 300,
            "min_instances": 1,
            "max_instances": 4 if peak_gap >= 40 else 2,
            "prefer_autoscaling": peak_gap >= 40 and not m["autoscaling_enabled"],
        },
        "notes": "Simulated policy only; no live cloud resources are changed.",
    }


TOOL_FUNCTIONS = {
    "get_resource_metrics": get_resource_metrics,
    "get_cost_estimate": get_cost_estimate,
    "get_service_level_targets": get_service_level_targets,
    "get_scaling_policy": get_scaling_policy,
}
