from __future__ import annotations

from .common import TraceRecord


def build_optimization_trace(baseline_trips: int, optimized_trips: int, distance_avoided_km: float) -> TraceRecord:
    return TraceRecord(
        agent_name="Optimization Agent",
        step_id="opt-001",
        input_summary=f"Baseline {baseline_trips} trips; optimized candidate {optimized_trips} trips.",
        tool_or_function_used="optimized scenario replay from plan_routes.csv",
        output_summary=f"Recommended plan consolidates {baseline_trips - optimized_trips} trips and avoids {distance_avoided_km:.2f} km.",
        decision_rationale="The hackathon prototype replays the deterministic optimized plan so impact remains stable and auditable.",
    )
