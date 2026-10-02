# User Edited Scenarios

This folder stores dispatch scenarios edited by users in the Streamlit dashboard.

Rules:

- Store each edited scenario as a JSON file.
- Do not overwrite files in `data/greendispatch-ai-dataset`.
- Do not include customer, confidential, personal, or client-branded data.
- Keep generated optimization outputs under `outputs/runs/<run_id>/`, not here.
- Use stable IDs for jobs, vehicles, locations, and scenarios.

Recommended file name:

```text
scenario_<timestamp_or_short_id>.json
```

Recommended module:

```text
src/core/scenario_store.py
```

The scenario JSON should contain metadata, jobs, vehicles, locations, distance matrix overrides if any, assumptions, and a reference to the source scenario.
