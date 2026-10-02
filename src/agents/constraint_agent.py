from __future__ import annotations

import pandas as pd

from .common import TraceRecord


def build_constraint_trace(constraint_results: pd.DataFrame) -> TraceRecord:
    failed = int((constraint_results["status"] != "pass").sum())
    total = len(constraint_results)
    status = "completed" if failed == 0 else "warning"
    return TraceRecord(
        agent_name="Constraint Agent",
        step_id="constraint-001",
        input_summary=f"Validated {total} routes for capacity, volume, SLA, availability, and priority.",
        tool_or_function_used="src.core.constraints.validate_routes",
        output_summary=f"{total - failed}/{total} routes passed constraints.",
        decision_rationale="Recommendations are not demo-ready until route feasibility is visible.",
        status=status,
    )
