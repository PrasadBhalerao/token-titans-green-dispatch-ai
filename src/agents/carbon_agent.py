from __future__ import annotations

from .common import TraceRecord


def build_carbon_trace(baseline_co2e: float, optimized_co2e: float) -> TraceRecord:
    avoided = round(baseline_co2e - optimized_co2e, 2)
    return TraceRecord(
        agent_name="Carbon Intelligence Agent",
        step_id="carbon-001",
        input_summary=f"Baseline {baseline_co2e:.2f} kgCO2e; optimized {optimized_co2e:.2f} kgCO2e.",
        tool_or_function_used="src.core.emissions + metrics_by_scenario.csv",
        output_summary=f"Estimated CO2e avoided: {avoided:.2f} kg.",
        decision_rationale="CO2e impact is quantified before the recommendation is sent for human review.",
    )
