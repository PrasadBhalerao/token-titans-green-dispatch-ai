from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = PROJECT_ROOT / "data" / "user-edited-scenarios"


def create_scenario_id(prefix: str = "scenario") -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{timestamp}"


def save_user_scenario(scenario_id: str, payload: dict[str, Any], scenario_dir: Path | str = SCENARIO_DIR) -> Path:
    path = Path(scenario_dir)
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f"{scenario_id}.json"
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return file_path


def load_user_scenario(scenario_id: str, scenario_dir: Path | str = SCENARIO_DIR) -> dict[str, Any]:
    file_path = Path(scenario_dir) / f"{scenario_id}.json"
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_user_scenarios(scenario_dir: Path | str = SCENARIO_DIR) -> list[str]:
    path = Path(scenario_dir)
    if not path.exists():
        return []
    return sorted(item.stem for item in path.glob("*.json") if item.name != "scenario-template.json")
