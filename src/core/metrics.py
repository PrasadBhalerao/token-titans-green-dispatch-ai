from __future__ import annotations

from typing import Any

import pandas as pd


METRIC_COLUMN_MAP = {
    "trips": "trips",
    "distance": "total_distance_km",
    "fuel": "total_fuel_liters",
    "energy": "total_energy_kwh",
    "co2e": "total_co2e_kg",
    "idle_time": "total_idle_minutes",
    "planning_time": "planning_time_minutes",
    "operating_cost_index": "operating_cost_index",
}


def calculate_capacity_utilization(total_demand_kg: float, capacity_kg: float) -> float:
    if capacity_kg <= 0:
        return 0.0
    return total_demand_kg / capacity_kg * 100


def calculate_reduction(baseline_value: float, optimized_value: float) -> dict[str, float]:
    absolute = baseline_value - optimized_value
    pct = 0.0 if baseline_value == 0 else absolute / baseline_value * 100
    return {"absolute_reduction": absolute, "reduction_pct": pct}


def calculate_scenario_metrics(
    routes: pd.DataFrame,
    reference_metrics: pd.DataFrame | None = None,
) -> pd.DataFrame:
    grouped = routes.groupby("scenario", as_index=False).agg(
        trips=("route_id", "count"),
        vehicles_used=("vehicle_id", "nunique"),
        total_distance_km=("total_distance_km", "sum"),
        total_fuel_liters=("fuel_liters", "sum"),
        total_energy_kwh=("energy_kwh", "sum"),
        total_co2e_kg=("co2e_kg", "sum"),
        total_idle_minutes=("idle_minutes", "sum"),
        total_travel_minutes=("travel_minutes", "sum"),
        total_service_minutes=("service_minutes", "sum"),
        avg_capacity_utilization_pct=("capacity_utilization_pct", "mean"),
        total_jobs=("job_count", "sum"),
        operating_cost_index=("operating_cost_index", "sum"),
    )

    grouped = grouped.round(
        {
            "total_distance_km": 2,
            "total_fuel_liters": 2,
            "total_energy_kwh": 2,
            "total_co2e_kg": 2,
            "avg_capacity_utilization_pct": 1,
            "operating_cost_index": 2,
        }
    )

    if reference_metrics is not None:
        reference_only = reference_metrics[
            [
                "scenario",
                "planning_time_minutes",
                "jobs_on_time",
                "total_jobs",
                "sla_adherence_pct",
            ]
        ].copy().rename(columns={"total_jobs": "reference_total_jobs"})
        grouped = grouped.merge(reference_only, on="scenario", how="left")
        extra_jobs = (grouped["total_jobs"] - grouped["reference_total_jobs"]).clip(lower=0)
        grouped["jobs_on_time"] = grouped["jobs_on_time"] + extra_jobs
        grouped["sla_adherence_pct"] = (grouped["jobs_on_time"] / grouped["total_jobs"] * 100).round(1)
        grouped = grouped.drop(columns=["reference_total_jobs"])
    else:
        grouped["planning_time_minutes"] = 0
        grouped["jobs_on_time"] = grouped["total_jobs"]
        grouped["sla_adherence_pct"] = 100.0

    ordered_columns = [
        "scenario",
        "trips",
        "vehicles_used",
        "total_distance_km",
        "total_fuel_liters",
        "total_energy_kwh",
        "total_co2e_kg",
        "total_idle_minutes",
        "total_travel_minutes",
        "total_service_minutes",
        "planning_time_minutes",
        "avg_capacity_utilization_pct",
        "jobs_on_time",
        "total_jobs",
        "sla_adherence_pct",
        "operating_cost_index",
    ]
    return grouped[ordered_columns]


def compare_scenarios(metrics: pd.DataFrame, baseline: str = "baseline", optimized: str = "optimized") -> pd.DataFrame:
    baseline_row = _scenario_row(metrics, baseline)
    optimized_row = _scenario_row(metrics, optimized)
    rows: list[dict[str, Any]] = []
    units = {
        "trips": "count",
        "distance": "km",
        "fuel": "liters",
        "energy": "kWh",
        "co2e": "kgCO2e",
        "idle_time": "minutes",
        "planning_time": "minutes",
        "operating_cost_index": "index",
    }
    for metric, column in METRIC_COLUMN_MAP.items():
        baseline_value = float(baseline_row[column])
        optimized_value = float(optimized_row[column])
        reduction = calculate_reduction(baseline_value, optimized_value)
        rows.append(
            {
                "comparison": f"{baseline}_vs_{optimized}",
                "metric": metric,
                "baseline": round(baseline_value, 2),
                "optimized": round(optimized_value, 2),
                "absolute_reduction": round(reduction["absolute_reduction"], 2),
                "reduction_pct": round(reduction["reduction_pct"], 1),
                "unit": units[metric],
            }
        )
    return pd.DataFrame(rows)


def build_decision_summary(
    metrics: pd.DataFrame,
    comparison: pd.DataFrame,
    approval_status: str,
    recommendation: str,
) -> dict[str, Any]:
    baseline = _scenario_row(metrics, "baseline")
    optimized = _scenario_row(metrics, "optimized")
    comparison_by_metric = comparison.set_index("metric").to_dict(orient="index")
    return {
        "approval_status": approval_status,
        "recommendation": recommendation,
        "baseline": _numeric_dict(baseline),
        "optimized": _numeric_dict(optimized),
        "reductions": comparison_by_metric,
        "headline": {
            "co2e_avoided_kg": comparison_by_metric["co2e"]["absolute_reduction"],
            "distance_avoided_km": comparison_by_metric["distance"]["absolute_reduction"],
            "fuel_saved_liters": comparison_by_metric["fuel"]["absolute_reduction"],
            "trips_consolidated": comparison_by_metric["trips"]["absolute_reduction"],
            "idle_minutes_reduced": comparison_by_metric["idle_time"]["absolute_reduction"],
        },
        "assumptions": [
            "Synthetic dispatch dataset only; no customer, confidential, personal, or client-branded data.",
            "Fuel and energy are calculated from distance, idle time, and documented vehicle rates.",
            "CO2e is calculated from included fuel and electricity emission factors.",
            "Agents recommend dispatch changes; humans approve before execution.",
        ],
    }


def _scenario_row(metrics: pd.DataFrame, scenario: str) -> pd.Series:
    row = metrics[metrics["scenario"] == scenario]
    if row.empty:
        raise ValueError(f"Metrics not found for scenario: {scenario}")
    return row.iloc[0]


def _numeric_dict(row: pd.Series) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in row.to_dict().items():
        if hasattr(value, "item"):
            value = value.item()
        output[key] = value
    return output
