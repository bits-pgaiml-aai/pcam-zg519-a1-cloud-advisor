from __future__ import annotations

import math
import random
from copy import deepcopy
from typing import Any

INSTANCE_CATALOG = {
    "t3.medium": {"vcpus": 2, "memory_gb": 4, "hourly_usd": 0.0416, "burst": True},
    "t3.large": {"vcpus": 2, "memory_gb": 8, "hourly_usd": 0.0832, "burst": True},
    "m5.large": {"vcpus": 2, "memory_gb": 8, "hourly_usd": 0.096, "burst": False},
    "m5.xlarge": {"vcpus": 4, "memory_gb": 16, "hourly_usd": 0.192, "burst": False},
    "m5.2xlarge": {"vcpus": 8, "memory_gb": 32, "hourly_usd": 0.384, "burst": False},
    "c5.xlarge": {"vcpus": 4, "memory_gb": 8, "hourly_usd": 0.170, "burst": False},
}

ACTIONS = (
    "keep_current",
    "scale_up",
    "scale_down",
    "enable_autoscaling",
    "rightsize_compute",
)

SLA_TARGETS = {
    "p95_response_ms": 300,
    "availability_pct": 99.5,
    "max_hourly_cost_usd": 0.25,
}

SCENARIOS: dict[str, dict[str, Any]] = {
    "A": {
        "id": "A",
        "name": "High CPU / slow responses",
        "kind": "critical",
        "description": (
            "CPU utilization is consistently high and response time exceeds target."
        ),
        "metrics": {
            "instance_type": "m5.large",
            "cpu_util_pct": 92.0,
            "memory_util_pct": 68.0,
            "p95_response_ms": 520.0,
            "error_rate_pct": 1.8,
            "requests_per_min": 420.0,
            "peak_cpu_util_pct": 96.0,
            "offpeak_cpu_util_pct": 88.0,
            "hourly_cost_usd": 0.096,
            "autoscaling_enabled": False,
            "availability_pct": 99.2,
        },
    },
    "B": {
        "id": "B",
        "name": "Over-provisioned expensive instance",
        "kind": "normal",
        "description": (
            "CPU and memory utilization are low, but the instance is expensive."
        ),
        "metrics": {
            "instance_type": "m5.2xlarge",
            "cpu_util_pct": 18.0,
            "memory_util_pct": 22.0,
            "p95_response_ms": 140.0,
            "error_rate_pct": 0.2,
            "requests_per_min": 95.0,
            "peak_cpu_util_pct": 28.0,
            "offpeak_cpu_util_pct": 8.0,
            "hourly_cost_usd": 0.384,
            "autoscaling_enabled": False,
            "availability_pct": 99.9,
        },
    },
    "C": {
        "id": "C",
        "name": "Sharp peak / off-peak variation",
        "kind": "normal",
        "description": "Workload varies sharply during peak and off-peak hours.",
        "metrics": {
            "instance_type": "m5.xlarge",
            "cpu_util_pct": 55.0,
            "memory_util_pct": 48.0,
            "p95_response_ms": 280.0,
            "error_rate_pct": 0.6,
            "requests_per_min": 260.0,
            "peak_cpu_util_pct": 91.0,
            "offpeak_cpu_util_pct": 12.0,
            "hourly_cost_usd": 0.192,
            "autoscaling_enabled": False,
            "availability_pct": 99.6,
        },
    },
    "D": {
        "id": "D",
        "name": "Ambiguous mixed signals",
        "kind": "edge",
        "description": (
            "Latency is slightly high, cost is near budget, and CPU is moderate "
            "with intermittent spikes."
        ),
        "metrics": {
            "instance_type": "c5.xlarge",
            "cpu_util_pct": 64.0,
            "memory_util_pct": 71.0,
            "p95_response_ms": 330.0,
            "error_rate_pct": 0.9,
            "requests_per_min": 310.0,
            "peak_cpu_util_pct": 84.0,
            "offpeak_cpu_util_pct": 35.0,
            "hourly_cost_usd": 0.170,
            "autoscaling_enabled": True,
            "availability_pct": 99.4,
        },
    },
}


def estimate_monthly_cost(hourly_usd: float) -> float:
    return round(hourly_usd * 24 * 30, 2)


def build_timeseries(metrics: dict[str, Any], seed: int = 42) -> dict[str, list[float]]:
    rng = random.Random(seed)
    cpu_now = metrics["cpu_util_pct"]
    peak = metrics["peak_cpu_util_pct"]
    offpeak = metrics["offpeak_cpu_util_pct"]
    p95 = metrics["p95_response_ms"]
    cpu_series = []
    rt_series = []
    for hour in range(24):
        day_factor = 0.55 + 0.45 * abs(math.sin((hour - 8) / 24 * math.pi))
        cpu = offpeak + (peak - offpeak) * day_factor
        cpu = max(1.0, min(99.0, cpu + rng.uniform(-3.0, 3.0)))
        # Pull series toward the reported "now" point near the end of the day.
        if hour >= 18:
            cpu = 0.7 * cpu + 0.3 * cpu_now
        rt = p95 * (0.85 + 0.3 * (cpu / max(peak, 1.0))) + rng.uniform(-8.0, 8.0)
        cpu_series.append(round(cpu, 1))
        rt_series.append(round(max(10.0, rt), 1))
    return {"hour": list(range(24)), "cpu_pct": cpu_series, "response_ms": rt_series}


def candidate_configs(current_instance: str) -> list[dict[str, Any]]:
    current = INSTANCE_CATALOG[current_instance]
    configs = []
    for name, spec in INSTANCE_CATALOG.items():
        configs.append(
            {
                "instance_type": name,
                "vcpus": spec["vcpus"],
                "memory_gb": spec["memory_gb"],
                "hourly_usd": spec["hourly_usd"],
                "monthly_usd": estimate_monthly_cost(spec["hourly_usd"]),
                "delta_vs_current_hourly": round(
                    spec["hourly_usd"] - current["hourly_usd"], 4
                ),
                "is_current": name == current_instance,
            }
        )
    return configs


def summarize_state(percept: dict[str, Any]) -> str:
    m = percept["metrics"]
    sla = percept["sla"]
    breaches = []
    if m["p95_response_ms"] > sla["p95_response_ms"]:
        breaches.append("latency>SLA")
    if m["availability_pct"] < sla["availability_pct"]:
        breaches.append("availability<SLA")
    if m["hourly_cost_usd"] > sla["max_hourly_cost_usd"]:
        breaches.append("cost>budget")
    breach_txt = ", ".join(breaches) if breaches else "no hard SLA breach"
    return (
        f"{percept['scenario_name']}: instance={m['instance_type']}, "
        f"cpu={m['cpu_util_pct']}%, mem={m['memory_util_pct']}%, "
        f"p95={m['p95_response_ms']}ms, cost=${m['hourly_cost_usd']}/hr, "
        f"autoscaling={m['autoscaling_enabled']} ({breach_txt})"
    )


class CloudWorld:
    def __init__(self) -> None:
        self.scenarios = deepcopy(SCENARIOS)

    def list_scenarios(self) -> list[dict[str, str]]:
        return [
            {
                "id": s["id"],
                "name": s["name"],
                "kind": s["kind"],
                "description": s["description"],
            }
            for s in self.scenarios.values()
        ]

    def get_scenario(self, scenario_id: str) -> dict[str, Any]:
        key = scenario_id.upper()
        if key not in self.scenarios:
            raise KeyError(f"Unknown scenario: {scenario_id}")
        return deepcopy(self.scenarios[key])

    def perceive(self, scenario_id: str) -> dict[str, Any]:
        scenario = self.get_scenario(scenario_id)
        metrics = scenario["metrics"]
        series = build_timeseries(metrics, seed=ord(scenario["id"][0]))
        recent = series["cpu_pct"][-6:]
        return {
            "scenario_id": scenario["id"],
            "scenario_name": scenario["name"],
            "scenario_kind": scenario["kind"],
            "description": scenario["description"],
            "metrics": metrics,
            "sla": deepcopy(SLA_TARGETS),
            "candidates": candidate_configs(metrics["instance_type"]),
            "catalog": deepcopy(INSTANCE_CATALOG),
            "timeseries": series,
            "kpis": {
                "instance": metrics["instance_type"],
                "monthly_cost_usd": estimate_monthly_cost(metrics["hourly_cost_usd"]),
                "cpu_now_pct": metrics["cpu_util_pct"],
                "cpu_avg_6h_pct": round(sum(recent) / len(recent), 1),
                "cpu_limit_pct": 80.0,
                "response_now_ms": round(series["response_ms"][-1], 1),
                "p95_response_ms": metrics["p95_response_ms"],
                "response_target_ms": SLA_TARGETS["p95_response_ms"],
                "availability_pct": metrics["availability_pct"],
                "availability_target_pct": SLA_TARGETS["availability_pct"],
            },
        }
