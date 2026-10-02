from __future__ import annotations

from dataclasses import asdict, dataclass


TRACE_FIELDS = [
    "agent_name",
    "step_id",
    "input_summary",
    "tool_or_function_used",
    "output_summary",
    "decision_rationale",
    "status",
]


@dataclass(frozen=True)
class TraceRecord:
    agent_name: str
    step_id: str
    input_summary: str
    tool_or_function_used: str
    output_summary: str
    decision_rationale: str
    status: str = "completed"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
