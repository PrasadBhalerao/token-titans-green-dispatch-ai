from __future__ import annotations

from .common import TraceRecord


def build_forecasting_trace(total_jobs: int, high_priority_jobs: int) -> TraceRecord:
    pressure = "high" if high_priority_jobs >= 4 else "normal"
    return TraceRecord(
        agent_name="Forecasting Agent",
        step_id="forecast-001",
        input_summary=f"{total_jobs} jobs, {high_priority_jobs} high/urgent priority jobs.",
        tool_or_function_used="jobs.csv demand and priority scan",
        output_summary=f"Workload pressure classified as {pressure}.",
        decision_rationale="Priority mix and job count guide consolidation and SLA checks.",
    )
