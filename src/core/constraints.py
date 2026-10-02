from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

import pandas as pd


DEFAULT_ROUTE_START = "09:00"
VOLUME_TOLERANCE_PCT = 0.05


def validate_routes(
    routes: pd.DataFrame,
    vehicles: pd.DataFrame,
    jobs: pd.DataFrame,
    unavailable_vehicle_ids: Iterable[str] | None = None,
    route_start_time: str = DEFAULT_ROUTE_START,
) -> pd.DataFrame:
    unavailable = set(unavailable_vehicle_ids or [])
    vehicle_lookup = vehicles.set_index("vehicle_id").to_dict(orient="index")
    job_lookup = jobs.set_index("job_id").to_dict(orient="index")
    results: list[dict[str, object]] = []

    for _, route in routes.iterrows():
        reasons: list[str] = []
        vehicle_id = str(route["vehicle_id"])
        vehicle = vehicle_lookup.get(vehicle_id)
        job_ids = _split_ids(str(route.get("job_ids", "")))

        if vehicle is None:
            reasons.append(f"Vehicle {vehicle_id} not found.")
            capacity_ok = False
            volume_ok = False
        else:
            capacity_ok = float(route["total_demand_kg"]) <= float(vehicle["capacity_kg"])
            volume_ok = float(route["total_volume_m3"]) <= float(vehicle["capacity_m3"]) * (1 + VOLUME_TOLERANCE_PCT)
            if not capacity_ok:
                reasons.append("Demand exceeds vehicle weight capacity.")
            if not volume_ok:
                reasons.append("Volume exceeds vehicle capacity.")

        vehicle_available = vehicle_id not in unavailable
        if not vehicle_available:
            reasons.append(f"Vehicle {vehicle_id} is unavailable.")

        all_jobs_found = all(job_id in job_lookup for job_id in job_ids)
        if not all_jobs_found:
            missing = [job_id for job_id in job_ids if job_id not in job_lookup]
            reasons.append(f"Missing jobs: {', '.join(missing)}.")

        sla_ok = _route_completion_within_due_time(route, job_ids, job_lookup, route_start_time)
        if not sla_ok:
            reasons.append("Route completion exceeds the earliest assigned job due time.")

        priority_ok = _priority_jobs_present(job_ids, job_lookup)
        if not priority_ok:
            reasons.append("Priority job check failed.")

        status = "pass" if not reasons else "fail"
        results.append(
            {
                "scenario": route["scenario"],
                "route_id": route["route_id"],
                "vehicle_id": vehicle_id,
                "status": status,
                "capacity_ok": capacity_ok,
                "volume_ok": volume_ok,
                "sla_ok": sla_ok,
                "vehicle_available": vehicle_available,
                "priority_ok": priority_ok,
                "reasons": "All constraints passed." if not reasons else " ".join(reasons),
            }
        )

    return pd.DataFrame(results)


def _split_ids(value: str) -> list[str]:
    return [part for part in value.split("|") if part]


def _route_completion_within_due_time(
    route: pd.Series,
    job_ids: list[str],
    job_lookup: dict[str, dict[str, object]],
    route_start_time: str,
) -> bool:
    if not job_ids:
        return False
    start = _parse_time(route_start_time)
    completion = start + timedelta(minutes=float(route.get("total_route_minutes", 0)))
    due_times = [_parse_time(str(job_lookup[job_id]["due_time"])) for job_id in job_ids if job_id in job_lookup]
    if not due_times:
        return False
    return completion <= min(due_times)


def _priority_jobs_present(job_ids: list[str], job_lookup: dict[str, dict[str, object]]) -> bool:
    for job_id in job_ids:
        job = job_lookup.get(job_id)
        if job is None:
            return False
        priority = str(job.get("priority", "")).lower()
        if priority in {"high", "urgent"} and job_id not in job_ids:
            return False
    return True


def _parse_time(value: str) -> datetime:
    return datetime.strptime(value, "%H:%M")
