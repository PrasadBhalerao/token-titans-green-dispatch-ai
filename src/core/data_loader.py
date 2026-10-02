from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = PROJECT_ROOT / "data" / "greendispatch-ai-dataset"

REQUIRED_FILES = {
    "locations": "locations.csv",
    "jobs": "jobs.csv",
    "vehicles": "vehicles.csv",
    "distance_matrix": "distance_matrix.csv",
    "emission_factors": "emission_factors.csv",
    "fuel_usage_profiles": "fuel_usage_profiles.csv",
    "plan_routes": "plan_routes.csv",
    "plan_legs": "plan_legs.csv",
    "plan_assignments": "plan_assignments.csv",
    "metrics_by_scenario": "metrics_by_scenario.csv",
    "metrics_comparison": "metrics_comparison.csv",
    "disruption_events": "disruption_events.csv",
    "standard_dataset_sources": "standard_dataset_sources.csv",
}

REQUIRED_COLUMNS = {
    "locations": {"location_id", "name", "zone", "x_km", "y_km", "location_type"},
    "jobs": {
        "job_id",
        "destination_id",
        "job_type",
        "demand_kg",
        "volume_m3",
        "priority",
        "ready_time",
        "due_time",
        "service_minutes",
    },
    "vehicles": {
        "vehicle_id",
        "vehicle_name",
        "vehicle_class",
        "energy_type",
        "capacity_kg",
        "capacity_m3",
        "fuel_rate_l_per_100km",
        "energy_rate_kwh_per_100km",
        "idle_fuel_l_per_hour",
        "idle_energy_kwh_per_hour",
        "co2e_factor",
        "co2e_factor_unit",
        "operating_cost_per_km",
        "rate_basis",
    },
    "distance_matrix": {"from_location_id", "to_location_id", "distance_km", "travel_minutes", "method"},
    "emission_factors": {"factor_id", "activity", "value", "unit", "scope", "source", "source_url", "usage_note"},
    "fuel_usage_profiles": {
        "profile_id",
        "vehicle_class",
        "energy_type",
        "low_realistic",
        "typical",
        "high_realistic",
        "unit",
        "demo_value_used",
        "basis",
    },
    "plan_routes": {
        "scenario",
        "route_id",
        "vehicle_id",
        "stop_sequence",
        "job_ids",
        "job_count",
        "total_demand_kg",
        "total_volume_m3",
        "capacity_utilization_pct",
        "total_distance_km",
        "travel_minutes",
        "service_minutes",
        "idle_minutes",
        "total_route_minutes",
        "fuel_liters",
        "energy_kwh",
        "co2e_kg",
        "operating_cost_index",
        "plan_note",
    },
    "plan_legs": {
        "scenario",
        "route_id",
        "vehicle_id",
        "leg_sequence",
        "from_location_id",
        "to_location_id",
        "distance_km",
        "travel_minutes",
    },
    "plan_assignments": {"scenario", "route_id", "vehicle_id", "job_id", "destination_id"},
    "metrics_by_scenario": {
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
    },
    "metrics_comparison": {
        "comparison",
        "metric",
        "baseline",
        "optimized",
        "absolute_reduction",
        "reduction_pct",
        "unit",
    },
    "disruption_events": {
        "event_id",
        "event_type",
        "event_time",
        "affected_vehicle_id",
        "description",
        "agent_action",
        "output_scenario",
    },
}

NUMERIC_COLUMNS = {
    "locations": {"x_km", "y_km"},
    "jobs": {"demand_kg", "volume_m3", "service_minutes"},
    "vehicles": {
        "capacity_kg",
        "capacity_m3",
        "fuel_rate_l_per_100km",
        "energy_rate_kwh_per_100km",
        "idle_fuel_l_per_hour",
        "idle_energy_kwh_per_hour",
        "co2e_factor",
        "operating_cost_per_km",
    },
    "distance_matrix": {"distance_km", "travel_minutes"},
    "emission_factors": {"value"},
    "fuel_usage_profiles": {"low_realistic", "typical", "high_realistic"},
    "plan_routes": {
        "job_count",
        "total_demand_kg",
        "total_volume_m3",
        "capacity_utilization_pct",
        "total_distance_km",
        "travel_minutes",
        "service_minutes",
        "idle_minutes",
        "total_route_minutes",
        "fuel_liters",
        "energy_kwh",
        "co2e_kg",
        "operating_cost_index",
    },
    "plan_legs": {"leg_sequence", "distance_km", "travel_minutes"},
    "metrics_by_scenario": {
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
    },
    "metrics_comparison": {"baseline", "optimized", "absolute_reduction", "reduction_pct"},
}


class DatasetValidationError(ValueError):
    """Raised when the local synthetic dataset is incomplete or malformed."""


@dataclass(frozen=True)
class DispatchDataset:
    dataset_dir: Path
    tables: dict[str, pd.DataFrame]
    scenarios: dict[str, Any]

    def table(self, name: str) -> pd.DataFrame:
        if name not in self.tables:
            raise KeyError(f"Unknown dataset table: {name}")
        return self.tables[name].copy()

    def row_counts(self) -> dict[str, int]:
        return {name: len(df) for name, df in self.tables.items()}

    def scenario_rows(self, table_name: str, scenario: str) -> pd.DataFrame:
        df = self.table(table_name)
        if "scenario" not in df.columns:
            raise DatasetValidationError(f"Table {table_name} does not include a scenario column.")
        return df[df["scenario"] == scenario].copy()

    def scenario_metrics(self, scenario: str) -> dict[str, Any]:
        metrics = self.table("metrics_by_scenario")
        row = metrics[metrics["scenario"] == scenario]
        if row.empty:
            raise DatasetValidationError(f"Metrics not found for scenario: {scenario}")
        return row.iloc[0].to_dict()

    def comparison_rows(self, comparison: str = "baseline_vs_optimized") -> pd.DataFrame:
        comparisons = self.table("metrics_comparison")
        return comparisons[comparisons["comparison"] == comparison].copy()


def load_dataset(dataset_dir: Path | str = DEFAULT_DATASET_DIR) -> DispatchDataset:
    dataset_path = Path(dataset_dir)
    validate_required_files(dataset_path)
    tables = {
        name: _load_csv(dataset_path / file_name, name)
        for name, file_name in REQUIRED_FILES.items()
    }
    validate_required_columns(tables)
    scenarios = _load_scenarios(dataset_path / "scenarios.json")
    return DispatchDataset(dataset_dir=dataset_path, tables=tables, scenarios=scenarios)


def validate_required_files(dataset_dir: Path) -> None:
    missing = [file_name for file_name in REQUIRED_FILES.values() if not (dataset_dir / file_name).exists()]
    if not (dataset_dir / "scenarios.json").exists():
        missing.append("scenarios.json")
    if missing:
        joined = ", ".join(sorted(missing))
        raise DatasetValidationError(f"Missing required dataset files: {joined}")


def validate_required_columns(tables: dict[str, pd.DataFrame]) -> None:
    errors: list[str] = []
    for name, expected in REQUIRED_COLUMNS.items():
        actual = set(tables[name].columns)
        missing = sorted(expected - actual)
        if missing:
            errors.append(f"{name}: missing columns {', '.join(missing)}")
    if errors:
        raise DatasetValidationError("; ".join(errors))


def _load_csv(path: Path, name: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in NUMERIC_COLUMNS.get(name, set()):
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    return df


def _load_scenarios(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
