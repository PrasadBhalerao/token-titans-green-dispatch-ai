from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "outputs" / "runs"


def create_run_id(prefix: str = "run") -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{timestamp}_{uuid4().hex[:8]}"


def save_run_artifact(run_id: str, name: str, payload: Any, runs_dir: Path | str = RUNS_DIR) -> Path:
    run_dir = Path(runs_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    artifact_name = name if name.endswith(".json") else f"{name}.json"
    path = run_dir / artifact_name
    with path.open("w", encoding="utf-8") as handle:
        json.dump(_to_jsonable(payload), handle, indent=2)
    return path


def load_run_artifact(run_id: str, name: str, runs_dir: Path | str = RUNS_DIR) -> Any:
    artifact_name = name if name.endswith(".json") else f"{name}.json"
    path = Path(runs_dir) / run_id / artifact_name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_runs(runs_dir: Path | str = RUNS_DIR) -> list[str]:
    path = Path(runs_dir)
    if not path.exists():
        return []
    return sorted([item.name for item in path.iterdir() if item.is_dir()])


def load_latest_run(runs_dir: Path | str = RUNS_DIR) -> dict[str, Any] | None:
    runs = list_runs(runs_dir)
    if not runs:
        return None
    latest = runs[-1]
    run_path = Path(runs_dir) / latest
    return {
        "run_id": latest,
        "artifacts": {
            artifact.stem: json.loads(artifact.read_text(encoding="utf-8"))
            for artifact in run_path.glob("*.json")
        },
    }


def save_run_bundle(run_id: str, artifacts: dict[str, Any], runs_dir: Path | str = RUNS_DIR) -> None:
    for name, payload in artifacts.items():
        save_run_artifact(run_id, name, payload, runs_dir)


def _to_jsonable(payload: Any) -> Any:
    if isinstance(payload, pd.DataFrame):
        return payload.to_dict(orient="records")
    if isinstance(payload, pd.Series):
        return payload.to_dict()
    if isinstance(payload, dict):
        return {str(key): _to_jsonable(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_to_jsonable(value) for value in payload]
    if hasattr(payload, "item"):
        return payload.item()
    if isinstance(payload, Path):
        return str(payload)
    return payload
