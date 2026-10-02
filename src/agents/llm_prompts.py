from __future__ import annotations

import json
from typing import Any

import pandas as pd


SYSTEM_PROMPT = """
You are GreenDispatch AI, a multi-agent dispatch optimization team.

Your agents are the Forecasting Agent, Carbon Intelligence Agent, Optimization
Agent, Constraint Agent, Monitoring Agent, and Orchestrator Agent.

Use the supplied JSON only. Do not invent vehicles, locations, jobs, routes,
metrics, emission factors, or constraints. Return JSON only.
""".strip()


def build_dispatch_optimizer_prompt(
    objective: str,
    jobs: pd.DataFrame,
    vehicles: pd.DataFrame,
    routes: pd.DataFrame,
    metrics: pd.DataFrame,
    constraints_summary: dict[str, Any],
) -> str:
    payload = {
        "requested_objective": _objective_label(objective),
        "allowed_scenarios": sorted(routes["scenario"].astype(str).unique().tolist()),
        "jobs": _records(jobs),
        "vehicles": _records(
            vehicles[
                [
                    "vehicle_id",
                    "vehicle_name",
                    "energy_type",
                    "capacity_kg",
                    "capacity_m3",
                    "fuel_rate_l_per_100km",
                    "energy_rate_kwh_per_100km",
                    "idle_fuel_l_per_hour",
                    "idle_energy_kwh_per_hour",
                    "co2e_factor",
                    "operating_cost_per_km",
                ]
            ]
        ),
        "candidate_route_plans": _records(routes),
        "scenario_metrics": _records(metrics),
        "constraints_summary": constraints_summary,
        "response_schema": {
            "recommended_scenario": "One allowed scenario id.",
            "recommendation": "Short recommendation for the dispatch planner.",
            "agent_outputs": [
                {
                    "agent_name": "Forecasting Agent",
                    "output_summary": "Agent conclusion.",
                    "decision_rationale": "Why it matters.",
                }
            ],
            "risks_or_tradeoffs": ["Important tradeoff."],
            "human_approval_note": "What the approver should verify.",
        },
    }
    return json.dumps(payload, indent=2)


def _objective_label(objective: str) -> str:
    labels = {
        "baseline": "review manual baseline only",
        "optimized": "balance CO2e, fuel, distance, cost, utilization, and SLA",
        "fuel_optimized": "minimize liquid fuel consumption",
        "distance_optimized": "minimize total distance",
        "reoptimized": "recover from disruption while preserving constraints",
    }
    return labels.get(objective, objective)


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records"))
