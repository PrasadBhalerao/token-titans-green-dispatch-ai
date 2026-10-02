from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.agents.carbon_agent import build_carbon_trace
from src.agents.common import TraceRecord
from src.agents.constraint_agent import build_constraint_trace
from src.agents.forecasting_agent import build_forecasting_trace
from src.agents.llm_optimizer import build_llm_not_requested_result, run_live_llm_optimizer
from src.agents.monitoring_agent import build_monitoring_trace
from src.agents.optimization_agent import build_optimization_trace
from src.core.constraints import validate_routes
from src.core.data_loader import DispatchDataset
from src.core.emissions import calculate_route_energy_and_emissions
from src.core.metrics import build_decision_summary, calculate_scenario_metrics, compare_scenarios
from src.core.plan_store import create_run_id, save_run_bundle


DEFAULT_RECOMMENDATION = (
    "Recommend the optimized dispatch plan for human review: it consolidates trips, "
    "reduces distance, lowers fuel use, and avoids CO2e while preserving constraints."
)


def run_dispatch_workflow(
    dataset: DispatchDataset,
    edited_jobs: pd.DataFrame | None = None,
    edited_vehicles: pd.DataFrame | None = None,
    approval_status: str = "needs_human_review",
    persist: bool = True,
    optimization_objective: str = "optimized",
    use_live_llm: bool = True,
) -> dict[str, Any]:
    source_jobs = dataset.table("jobs")
    routes = dataset.table("plan_routes")
    jobs = _normalize_jobs(edited_jobs) if edited_jobs is not None else source_jobs
    vehicles = _normalize_vehicles(edited_vehicles) if edited_vehicles is not None else dataset.table("vehicles")
    assignments = dataset.table("plan_assignments")
    disruption_events = dataset.table("disruption_events")
    reference_metrics = dataset.table("metrics_by_scenario")
    new_jobs = _new_jobs(source_jobs, jobs)

    if not new_jobs.empty:
        routes, assignments = _append_new_workload_routes(
            routes=routes,
            assignments=assignments,
            new_jobs=new_jobs,
            vehicles=vehicles,
            distance_matrix=dataset.table("distance_matrix"),
        )

    metrics = calculate_scenario_metrics(routes, reference_metrics)
    comparison = _prefer_reference_comparison(dataset.table("metrics_comparison"), metrics, has_edits=not new_jobs.empty)

    baseline_routes = routes[routes["scenario"] == "baseline"].copy()
    optimized_routes = routes[routes["scenario"] == "optimized"].copy()
    reoptimized_routes = routes[routes["scenario"] == "reoptimized"].copy()
    optimized_constraints = validate_routes(optimized_routes, vehicles, jobs)

    disruption_event = disruption_events.iloc[0].to_dict() if not disruption_events.empty else {}
    reoptimized_constraints = validate_routes(
        reoptimized_routes,
        vehicles,
        jobs,
        unavailable_vehicle_ids=[str(disruption_event.get("affected_vehicle_id", ""))],
    )

    llm_result = _run_llm_layer(
        use_live_llm=use_live_llm,
        optimization_objective=optimization_objective,
        jobs=jobs,
        vehicles=vehicles,
        routes=routes,
        metrics=metrics,
        optimized_constraints=optimized_constraints,
        reoptimized_constraints=reoptimized_constraints,
    )
    trace = _build_trace(jobs, metrics, comparison, optimized_constraints, disruption_event, llm_result)
    sustainability = _build_agent_sustainability(comparison, trace, llm_result)
    approval_audit = _initial_approval_audit(approval_status)
    decision_summary = build_decision_summary(
        metrics=metrics,
        comparison=comparison,
        approval_status=approval_status,
        recommendation=_recommendation_text(llm_result),
    )

    run_id = create_run_id()
    artifacts = {
        "run_metadata": {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "dataset_dir": str(dataset.dataset_dir),
            "status": approval_status,
            "source": "synthetic demo dataset",
            "new_workload_jobs": len(new_jobs),
            "execution_mode": sustainability["execution_mode"],
            "optimization_objective": optimization_objective,
        },
        "agent_trace": trace,
        "baseline_plan": baseline_routes,
        "edited_jobs": jobs,
        "edited_vehicles": vehicles,
        "candidate_plans": _candidate_plan_artifacts(routes),
        "optimized_plan": optimized_routes,
        "constraint_results": optimized_constraints,
        "metrics_summary": metrics,
        "metrics_comparison": comparison,
        "disruption_event": disruption_event,
        "reoptimized_plan": reoptimized_routes,
        "reoptimized_constraint_results": reoptimized_constraints,
        "approval_audit": approval_audit,
        "decision_summary": decision_summary,
        "agent_sustainability": sustainability,
        "llm_optimizer_result": llm_result,
    }
    if persist:
        save_run_bundle(run_id, artifacts)

    return {
        "run_id": run_id,
        "routes": routes,
        "assignments": assignments,
        "jobs": jobs,
        "vehicles": vehicles,
        "metrics": metrics,
        "comparison": comparison,
        "optimized_constraints": optimized_constraints,
        "reoptimized_constraints": reoptimized_constraints,
        "disruption_event": disruption_event,
        "trace": trace,
        "agent_sustainability": sustainability,
        "llm_optimizer_result": llm_result,
        "approval_audit": approval_audit,
        "decision_summary": decision_summary,
    }


def apply_approval_decision(workflow: dict[str, Any], decision: str, note: str = "") -> dict[str, Any]:
    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "note": note,
        "actor": "human_dispatch_planner",
    }
    workflow = dict(workflow)
    workflow["approval_audit"] = list(workflow.get("approval_audit", [])) + [audit_entry]
    workflow["decision_summary"] = dict(workflow["decision_summary"])
    workflow["decision_summary"]["approval_status"] = decision
    return workflow


def _build_trace(
    jobs: pd.DataFrame,
    metrics: pd.DataFrame,
    comparison: pd.DataFrame,
    constraint_results: pd.DataFrame,
    disruption_event: dict[str, Any],
    llm_result: dict[str, Any],
) -> list[dict[str, str]]:
    high_priority = int(jobs["priority"].isin(["high", "urgent"]).sum())
    total_jobs = len(jobs)
    metric_lookup = metrics.set_index("scenario").to_dict(orient="index")
    comparison_lookup = comparison.set_index("metric").to_dict(orient="index")
    records: list[TraceRecord] = [
        TraceRecord(
            agent_name="Orchestrator Agent",
            step_id="orchestrator-001",
            input_summary=f"Loaded {total_jobs} jobs, vehicles, route plans, metrics, and disruption scenario.",
            tool_or_function_used="src.core.data_loader.load_dataset",
            output_summary="Prepared baseline, optimized, and reoptimized workflow inputs.",
            decision_rationale="The orchestrator coordinates deterministic tools and agent-specific reasoning.",
        ),
        build_forecasting_trace(total_jobs=total_jobs, high_priority_jobs=high_priority),
        build_carbon_trace(
            baseline_co2e=float(metric_lookup["baseline"]["total_co2e_kg"]),
            optimized_co2e=float(metric_lookup["optimized"]["total_co2e_kg"]),
        ),
        build_optimization_trace(
            baseline_trips=int(metric_lookup["baseline"]["trips"]),
            optimized_trips=int(metric_lookup["optimized"]["trips"]),
            distance_avoided_km=float(comparison_lookup["distance"]["absolute_reduction"]),
        ),
        build_constraint_trace(constraint_results),
        build_monitoring_trace(disruption_event),
    ]
    records.extend(_llm_trace_records(llm_result))
    return [record.to_dict() for record in records]


def _build_agent_sustainability(
    comparison: pd.DataFrame,
    trace: list[dict[str, str]],
    llm_result: dict[str, Any],
) -> dict[str, Any]:
    comparison_lookup = comparison.set_index("metric").to_dict(orient="index")
    token_usage = llm_result.get("token_usage", {})
    model_calls = int(llm_result.get("model_calls", 0))
    total_tokens = int(token_usage.get("total_tokens", 0))
    input_tokens = int(token_usage.get("input_tokens", 0))
    output_tokens = int(token_usage.get("output_tokens", 0))
    deterministic_calculators = [
        "emissions",
        "metrics",
        "constraints",
        "scenario comparison",
        "plan persistence",
    ]
    tool_calls = len(trace) + len(deterministic_calculators)
    retries = int(llm_result.get("retries", 0))
    cache_reuse_count = 0
    co2e_avoided = float(comparison_lookup["co2e"]["absolute_reduction"])
    distance_avoided = float(comparison_lookup["distance"]["absolute_reduction"])
    per_model_co2e = round(co2e_avoided / model_calls, 2) if model_calls else 0
    per_model_distance = round(distance_avoided / model_calls, 2) if model_calls else 0
    execution_mode = "live_openai_llm" if llm_result.get("used_llm") else "deterministic_fallback"
    return {
        "execution_mode": execution_mode,
        "llm_status": llm_result.get("status", "unknown"),
        "model": llm_result.get("model", ""),
        "model_calls": model_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_tokens": total_tokens,
        "tool_calls": tool_calls,
        "retries": retries,
        "deterministic_calculators_used": len(deterministic_calculators),
        "cache_reuse_count": cache_reuse_count,
        "co2e_avoided_per_model_call_kg": per_model_co2e,
        "distance_avoided_per_model_call_km": per_model_distance,
        "trace_steps": len(trace),
        "fallback_reason": llm_result.get("fallback_reason", ""),
        "recommended_scenario": llm_result.get("recommended_scenario", ""),
        "explanation": (
            _sustainability_explanation(llm_result)
        ),
    }


def _run_llm_layer(
    use_live_llm: bool,
    optimization_objective: str,
    jobs: pd.DataFrame,
    vehicles: pd.DataFrame,
    routes: pd.DataFrame,
    metrics: pd.DataFrame,
    optimized_constraints: pd.DataFrame,
    reoptimized_constraints: pd.DataFrame,
) -> dict[str, Any]:
    if not use_live_llm:
        return build_llm_not_requested_result()
    return run_live_llm_optimizer(
        objective=optimization_objective,
        jobs=jobs,
        vehicles=vehicles,
        routes=routes,
        metrics=metrics,
        constraints_summary=_constraint_summary(
            optimized_constraints=optimized_constraints,
            reoptimized_constraints=reoptimized_constraints,
        ),
    )


def _candidate_plan_artifacts(routes: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    candidates: dict[str, list[dict[str, Any]]] = {}
    for scenario in sorted(routes["scenario"].astype(str).unique()):
        if scenario == "baseline":
            continue
        candidates[scenario] = routes[routes["scenario"] == scenario].to_dict(orient="records")
    return candidates


def _constraint_summary(
    optimized_constraints: pd.DataFrame,
    reoptimized_constraints: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "optimized": _constraint_counts(optimized_constraints),
        "reoptimized": _constraint_counts(reoptimized_constraints),
    }


def _constraint_counts(constraints: pd.DataFrame) -> dict[str, int]:
    total = len(constraints)
    failed = int((constraints["status"] != "pass").sum()) if total else 0
    return {
        "total_routes": total,
        "passed_routes": total - failed,
        "failed_routes": failed,
    }


def _llm_trace_records(llm_result: dict[str, Any]) -> list[TraceRecord]:
    token_usage = llm_result.get("token_usage", {})
    if not llm_result.get("used_llm"):
        return [
            TraceRecord(
                agent_name="Live LLM Agent Layer",
                step_id="llm-000",
                input_summary="Checked whether a live OpenAI optimizer should run.",
                tool_or_function_used="OPENAI_API_KEY environment lookup",
                output_summary=f"Used deterministic fallback: {llm_result.get('status')}.",
                decision_rationale=str(llm_result.get("fallback_reason", "Live LLM was not used.")),
                status="warning",
            )
        ]

    records = [
        TraceRecord(
            agent_name="Live LLM Orchestrator",
            step_id="llm-001",
            input_summary="Candidate route plans, jobs, vehicles, metrics, and constraints.",
            tool_or_function_used=f"OpenAI API model {llm_result.get('model')}",
            output_summary=str(llm_result.get("recommendation", "")),
            decision_rationale=(
                f"Live response consumed {token_usage.get('total_tokens', 0)} tokens "
                "and was grounded by deterministic calculators."
            ),
        )
    ]
    for index, agent_output in enumerate(llm_result.get("agent_outputs", []), start=2):
        if not isinstance(agent_output, dict):
            continue
        records.append(
            TraceRecord(
                agent_name=str(agent_output.get("agent_name", f"LLM Agent {index}")),
                step_id=f"llm-{index:03d}",
                input_summary="Live LLM agent output from the reusable dispatch optimizer prompt.",
                tool_or_function_used=f"OpenAI API model {llm_result.get('model')}",
                output_summary=str(agent_output.get("output_summary", "")),
                decision_rationale=str(agent_output.get("decision_rationale", "")),
            )
        )
    return records


def _recommendation_text(llm_result: dict[str, Any]) -> str:
    if llm_result.get("used_llm") and llm_result.get("recommendation"):
        return str(llm_result["recommendation"])
    return DEFAULT_RECOMMENDATION


def _sustainability_explanation(llm_result: dict[str, Any]) -> str:
    if llm_result.get("used_llm"):
        return (
            "Live OpenAI agents evaluated the candidate plans, while deterministic calculators "
            "kept emissions, metrics, and constraints auditable. Token counts come directly "
            "from the OpenAI API response usage metadata."
        )
    reason = llm_result.get("fallback_reason") or "Live LLM was not used."
    return (
        f"Deterministic fallback used. {reason} Emissions, metrics, and constraints "
        "were still calculated with local deterministic tools, and actual LLM tokens are zero."
    )


def _initial_approval_audit(status: str) -> list[dict[str, str]]:
    return [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": status,
            "note": "Optimized plan generated and waiting for human review.",
            "actor": "system",
        }
    ]


def _prefer_reference_comparison(reference: pd.DataFrame, metrics: pd.DataFrame, has_edits: bool = False) -> pd.DataFrame:
    if not has_edits and not reference.empty:
        return reference.copy()
    return compare_scenarios(metrics)


def _normalize_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
    normalized = jobs.copy()
    numeric_columns = ["demand_kg", "volume_m3", "service_minutes"]
    for column in numeric_columns:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce").fillna(0)
    return normalized


def _normalize_vehicles(vehicles: pd.DataFrame) -> pd.DataFrame:
    normalized = vehicles.copy()
    numeric_columns = [
        "capacity_kg",
        "capacity_m3",
        "fuel_rate_l_per_100km",
        "energy_rate_kwh_per_100km",
        "idle_fuel_l_per_hour",
        "idle_energy_kwh_per_hour",
        "co2e_factor",
        "operating_cost_per_km",
    ]
    for column in numeric_columns:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce").fillna(0)
    return normalized


def _new_jobs(source_jobs: pd.DataFrame, edited_jobs: pd.DataFrame) -> pd.DataFrame:
    source_ids = set(source_jobs["job_id"].astype(str))
    edited = edited_jobs.copy()
    edited["job_id"] = edited["job_id"].astype(str)
    return edited[~edited["job_id"].isin(source_ids)].copy()


def _append_new_workload_routes(
    routes: pd.DataFrame,
    assignments: pd.DataFrame,
    new_jobs: pd.DataFrame,
    vehicles: pd.DataFrame,
    distance_matrix: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    route_rows: list[dict[str, Any]] = []
    assignment_rows: list[dict[str, Any]] = []

    for sequence, (_, job) in enumerate(new_jobs.iterrows(), start=1):
        baseline_vehicle = _choose_vehicle(job, vehicles, prefer_low_carbon=False)
        optimized_vehicle = _choose_vehicle(job, vehicles, prefer_low_carbon=True)

        route_rows.append(
            _build_new_route_row(
                scenario="baseline",
                route_id=f"B_NEW_{sequence:02d}",
                job=job,
                vehicle=baseline_vehicle,
                distance_matrix=distance_matrix,
                plan_note="New workload added as a manual-style incremental route.",
            )
        )
        route_rows.append(
            _build_new_route_row(
                scenario="optimized",
                route_id=f"O_NEW_{sequence:02d}",
                job=job,
                vehicle=optimized_vehicle,
                distance_matrix=distance_matrix,
                plan_note="New workload assigned by carbon-aware incremental optimizer.",
            )
        )
        route_rows.append(
            _build_new_route_row(
                scenario="fuel_optimized",
                route_id=f"F_NEW_{sequence:02d}",
                job=job,
                vehicle=optimized_vehicle,
                distance_matrix=distance_matrix,
                plan_note="New workload assigned by fuel-focused incremental optimizer.",
            )
        )
        route_rows.append(
            _build_new_route_row(
                scenario="distance_optimized",
                route_id=f"D_NEW_{sequence:02d}",
                job=job,
                vehicle=optimized_vehicle,
                distance_matrix=distance_matrix,
                plan_note="New workload assigned by distance-focused incremental optimizer.",
            )
        )
        route_rows.append(
            _build_new_route_row(
                scenario="reoptimized",
                route_id=f"R_NEW_{sequence:02d}",
                job=job,
                vehicle=optimized_vehicle,
                distance_matrix=distance_matrix,
                plan_note="New workload retained in reoptimized scenario.",
            )
        )

    for row in route_rows:
        assignment_rows.append(
            {
                "scenario": row["scenario"],
                "route_id": row["route_id"],
                "vehicle_id": row["vehicle_id"],
                "job_id": row["job_ids"],
                "destination_id": row["stop_sequence"].split("|")[1],
            }
        )

    updated_routes = pd.concat([routes, pd.DataFrame(route_rows)], ignore_index=True)
    updated_assignments = pd.concat([assignments, pd.DataFrame(assignment_rows)], ignore_index=True)
    return updated_routes, updated_assignments


def _choose_vehicle(job: pd.Series, vehicles: pd.DataFrame, prefer_low_carbon: bool) -> pd.Series:
    demand_kg = float(job["demand_kg"])
    volume_m3 = float(job["volume_m3"])
    feasible = vehicles[
        (vehicles["capacity_kg"] >= demand_kg)
        & (vehicles["capacity_m3"] * 1.05 >= volume_m3)
    ].copy()
    if feasible.empty:
        feasible = vehicles.copy()
    if prefer_low_carbon:
        feasible["_score"] = feasible["co2e_factor"].astype(float) * feasible["operating_cost_per_km"].astype(float)
        return feasible.sort_values(["_score", "operating_cost_per_km"]).iloc[0]
    non_electric = feasible[feasible["energy_type"].astype(str).str.lower() != "electric"]
    if not non_electric.empty:
        return non_electric.iloc[0]
    return feasible.iloc[0]


def _build_new_route_row(
    scenario: str,
    route_id: str,
    job: pd.Series,
    vehicle: pd.Series,
    distance_matrix: pd.DataFrame,
    plan_note: str,
) -> dict[str, Any]:
    destination_id = str(job["destination_id"])
    outbound = _distance_leg(distance_matrix, "DEPOT_A", destination_id)
    inbound = _distance_leg(distance_matrix, destination_id, "DEPOT_A")
    total_distance_km = round(outbound["distance_km"] + inbound["distance_km"], 2)
    travel_minutes = int(outbound["travel_minutes"] + inbound["travel_minutes"])
    idle_minutes = 5 if str(job.get("priority", "")).lower() != "urgent" else 3
    service_minutes = int(job["service_minutes"])
    route_stub = {
        "total_distance_km": total_distance_km,
        "idle_minutes": idle_minutes,
    }
    emissions = calculate_route_energy_and_emissions(route_stub, vehicle.to_dict())
    capacity_utilization = float(job["demand_kg"]) / float(vehicle["capacity_kg"]) * 100 if float(vehicle["capacity_kg"]) else 0
    operating_cost_index = total_distance_km * float(vehicle["operating_cost_per_km"])
    return {
        "scenario": scenario,
        "route_id": route_id,
        "vehicle_id": vehicle["vehicle_id"],
        "stop_sequence": f"DEPOT_A|{destination_id}|DEPOT_A",
        "job_ids": job["job_id"],
        "job_count": 1,
        "total_demand_kg": float(job["demand_kg"]),
        "total_volume_m3": float(job["volume_m3"]),
        "capacity_utilization_pct": round(capacity_utilization, 1),
        "total_distance_km": total_distance_km,
        "travel_minutes": travel_minutes,
        "service_minutes": service_minutes,
        "idle_minutes": idle_minutes,
        "total_route_minutes": travel_minutes + service_minutes + idle_minutes,
        "fuel_liters": round(emissions["fuel_liters"], 2),
        "energy_kwh": round(emissions["energy_kwh"], 2),
        "co2e_kg": round(emissions["co2e_kg"], 2),
        "operating_cost_index": round(operating_cost_index, 2),
        "plan_note": plan_note,
    }


def _distance_leg(distance_matrix: pd.DataFrame, origin: str, destination: str) -> dict[str, float]:
    row = distance_matrix[
        (distance_matrix["from_location_id"] == origin)
        & (distance_matrix["to_location_id"] == destination)
    ]
    if row.empty:
        raise ValueError(f"Missing distance matrix leg from {origin} to {destination}.")
    return {
        "distance_km": float(row.iloc[0]["distance_km"]),
        "travel_minutes": float(row.iloc[0]["travel_minutes"]),
    }
