from __future__ import annotations

import json
import os
from typing import Any

import pandas as pd

from src.agents.llm_prompts import SYSTEM_PROMPT, build_dispatch_optimizer_prompt


DEFAULT_MODEL = "gpt-4o-mini"
MODEL_ENV_VAR = "GREEN_DISPATCH_OPENAI_MODEL"


def run_live_llm_optimizer(
    objective: str,
    jobs: pd.DataFrame,
    vehicles: pd.DataFrame,
    routes: pd.DataFrame,
    metrics: pd.DataFrame,
    constraints_summary: dict[str, Any],
) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GREEN_DISPATCH_OPENAI_API_KEY")
    model = os.getenv(MODEL_ENV_VAR, DEFAULT_MODEL)
    if not api_key:
        return _fallback_result(
            status="missing_api_key",
            model=model,
            reason="OPENAI_API_KEY is not configured.",
        )

    try:
        from openai import OpenAI
    except ImportError:
        return _fallback_result(
            status="openai_sdk_missing",
            model=model,
            reason="The openai package is not installed. Run pip install -r requirements.txt.",
        )

    prompt = build_dispatch_optimizer_prompt(
        objective=objective,
        jobs=jobs,
        vehicles=vehicles,
        routes=routes,
        metrics=metrics,
        constraints_summary=constraints_summary,
    )

    try:
        client = OpenAI(api_key=api_key, timeout=30.0)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        content = response.choices[0].message.content or "{}"
        parsed = _parse_json_response(content)
        return {
            "used_llm": True,
            "status": "live_openai_llm",
            "model": model,
            "model_calls": 1,
            "retries": 0,
            "fallback_reason": "",
            "token_usage": _extract_usage(response),
            "raw_response": content,
            "parsed_response": parsed,
            "recommended_scenario": str(parsed.get("recommended_scenario", objective)),
            "recommendation": str(parsed.get("recommendation", "")),
            "agent_outputs": parsed.get("agent_outputs", []),
            "risks_or_tradeoffs": parsed.get("risks_or_tradeoffs", []),
            "human_approval_note": str(parsed.get("human_approval_note", "")),
        }
    except Exception as exc:  # pragma: no cover - depends on live API behavior
        return _fallback_result(
            status="openai_api_error",
            model=model,
            reason=f"{type(exc).__name__}: {exc}",
            model_calls=1,
        )


def build_llm_not_requested_result(reason: str = "Live LLM call was not requested for this refresh.") -> dict[str, Any]:
    return _fallback_result(
        status="not_requested",
        model=os.getenv(MODEL_ENV_VAR, DEFAULT_MODEL),
        reason=reason,
    )


def _fallback_result(
    status: str,
    model: str,
    reason: str,
    model_calls: int = 0,
) -> dict[str, Any]:
    return {
        "used_llm": False,
        "status": status,
        "model": model,
        "model_calls": model_calls,
        "retries": 0,
        "fallback_reason": reason,
        "token_usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
        "raw_response": "",
        "parsed_response": {},
        "recommended_scenario": "",
        "recommendation": "",
        "agent_outputs": [],
        "risks_or_tradeoffs": [],
        "human_approval_note": "",
    }


def _extract_usage(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    input_tokens = _usage_value(usage, "prompt_tokens", "input_tokens")
    output_tokens = _usage_value(usage, "completion_tokens", "output_tokens")
    total_tokens = _usage_value(usage, "total_tokens")
    if total_tokens == 0:
        total_tokens = input_tokens + output_tokens
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _usage_value(usage: Any, *names: str) -> int:
    if usage is None:
        return 0
    for name in names:
        if isinstance(usage, dict) and name in usage:
            return int(usage[name] or 0)
        value = getattr(usage, name, None)
        if value is not None:
            return int(value or 0)
    return 0


def _parse_json_response(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            parsed = json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            return {}
    return parsed if isinstance(parsed, dict) else {}
