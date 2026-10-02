from __future__ import annotations

from .common import TraceRecord


def build_monitoring_trace(event: dict[str, object]) -> TraceRecord:
    return TraceRecord(
        agent_name="Monitoring Agent",
        step_id="monitor-001",
        input_summary=f"{event.get('event_type')} at {event.get('event_time')} affecting {event.get('affected_vehicle_id')}.",
        tool_or_function_used="disruption_events.csv",
        output_summary=str(event.get("agent_action")),
        decision_rationale="The workflow demonstrates dynamic re-planning when operating conditions change.",
    )
