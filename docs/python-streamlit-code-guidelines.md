# Python and Streamlit Code Guidelines

Engineering standards and code review checklist for GreenDispatch AI.

## 1. Purpose

These guidelines keep the hackathon build fast, testable, and demo-ready while preserving the requirements in:

- `INSTRUCTIONS.md`
- `docs/greendispatch-ai-spec.md`
- `docs/greendispatch-ai-implementation-plan.md`
- `docs/hackathon-details.md`

The project is a Streamlit + Python prototype. Optimize for clarity, deterministic calculations, visible agent trace, and a reliable dashboard demo.

## 2. Technology Choices

Use this stack unless the team explicitly changes it:

| Layer | Technology |
| --- | --- |
| UI dashboard | Streamlit |
| App/core language | Python |
| Data handling | pandas |
| Charts | Plotly |
| Tests | pytest |
| Optimization | Explainable Python heuristics first; OR-Tools optional |
| Storage | Local CSV/JSON files |
| Run artifacts | `outputs/runs/<run_id>/` JSON files |

Avoid adding React, FastAPI, a database, or a paid map/routing dependency unless the spec is revised.

## 3. Project Structure Standards

Target layout:

```text
app.py
requirements.txt
data/
  greendispatch-ai-dataset/
docs/
src/
  agents/
  core/
  ui/
tests/
outputs/
  runs/
```

Rules:

- Keep deterministic calculations in `src/core`.
- Keep agent orchestration and agent trace logic in `src/agents`.
- Keep Streamlit rendering helpers in `src/ui`.
- Keep `app.py` thin: configure page, load data, call workflow, render sections.
- Do not put business logic inside Streamlit button callbacks if it can live in `src/core` or `src/agents`.

## 4. Python Standards

### 4.1 Style

- Use clear function and variable names.
- Prefer small functions with one responsibility.
- Add type hints for public functions.
- Use `pathlib.Path` for file paths.
- Use constants for scenario names, file names, and status values.
- Keep comments brief and useful.
- Avoid clever code in calculation paths.

Example:

```python
from pathlib import Path

DATASET_DIR = Path("data/greendispatch-ai-dataset")


def calculate_fuel_liters(distance_km: float, fuel_rate_l_per_100km: float, idle_minutes: float, idle_l_per_hour: float) -> float:
    driving_fuel = distance_km * fuel_rate_l_per_100km / 100
    idle_fuel = idle_minutes * idle_l_per_hour / 60
    return driving_fuel + idle_fuel
```

### 4.2 Data Handling

- Load CSV files with explicit expected columns.
- Validate required files and columns at startup.
- Treat all source data as synthetic demo data.
- Never introduce customer, confidential, personal, or client-branded data.
- Do not mutate raw loaded DataFrames in place; return transformed copies where practical.
- Use stable IDs: `job_id`, `vehicle_id`, `route_id`, `scenario`.

### 4.3 Calculations

- Calculation functions must be deterministic and unit-tested.
- Do not ask an LLM to do arithmetic that Python can do reliably.
- Keep emissions, metrics, constraints, and optimization scoring separate.
- Match dataset totals within documented rounding tolerance.
- Display:
  - distance, fuel, energy, CO2e, and cost index to 2 decimals
  - percentages to 1 decimal

### 4.4 Error Handling

- Fail early for missing required data files.
- Raise readable exceptions in core functions.
- In Streamlit, show user-friendly error messages with `st.error`.
- Do not hide calculation or data-validation failures.

### 4.5 Testing

Minimum tests:

- `tests/test_data_loading.py`
- `tests/test_emissions.py`
- `tests/test_metrics.py`
- `tests/test_constraints.py`
- `tests/test_agent_trace.py`

Tests must cover:

- required dataset files and columns
- emissions formulas
- baseline/optimized totals
- reduction percentages
- valid and invalid constraints
- required agent trace fields

## 5. Streamlit Standards

### 5.1 App Structure

Recommended `app.py` flow:

```python
import streamlit as st

from src.core.data_loader import load_dataset
from src.agents.orchestrator import run_optimization
from src.ui.dashboard import render_dashboard


st.set_page_config(page_title="GreenDispatch AI", layout="wide")

dataset = load_dataset()
render_dashboard(dataset)
```

Rules:

- `st.set_page_config` must be near the top of `app.py`.
- Use `st.sidebar` for scenario controls.
- Use tabs for major workflows: Baseline, Optimized, Agents, Disruption, Sustainability.
- Use `st.session_state` for user-edited scenario data and approval status.
- Use `st.form` for grouped user inputs.
- Use `st.data_editor` for editable jobs and vehicles.

### 5.2 Caching

Use Streamlit caching carefully:

- Use `@st.cache_data` for loading CSV/JSON data.
- Use `@st.cache_data` for deterministic metric calculations when input data is stable.
- Clear or bypass cache when user edits jobs/vehicles.
- Do not cache approval state.
- Do not cache anything that contains secrets or credentials.

### 5.3 UI Layout

The first screen must be the working dashboard, not a landing page.

Required dashboard sections:

- Scenario selector.
- Baseline vs optimized KPI cards.
- Route plan table.
- Job assignment table.
- Emissions and assumptions panel.
- Agent trace panel.
- Human approval panel.
- Disruption and re-optimization panel.
- Agent sustainability panel.
- Decision summary panel.

Lead with these KPIs:

- Trips reduced.
- Distance avoided.
- Fuel or energy saved.
- CO2e avoided.
- Idle or planning time reduced.

### 5.4 Styling

Streamlit styling is allowed, but keep it restrained and maintainable.

Acceptable:

- KPI cards.
- Status chips.
- Section headers.
- Light custom CSS.
- Plotly charts.
- Compact tables.

Rules:

- Keep CSS in one helper function or one clearly marked block.
- Do not scatter `unsafe_allow_html=True` throughout the app.
- Use accessible color contrast.
- Avoid decorative effects that distract from operational metrics.
- The dashboard should feel like an operations tool, not a marketing site.

### 5.5 Inputs

Streamlit can collect interactive inputs for jobs, vehicles, and disruptions.

Use:

- `st.form` for adding a new job.
- `st.data_editor` for editing job/vehicle tables.
- `st.selectbox` for scenario, vehicle, location, and priority.
- `st.number_input` for demand, capacity, fuel rate, energy rate, and service time.
- `st.time_input` for ready and due times.
- `st.button` for run optimization, trigger disruption, approve, reject, and request revision.

Validate user input before running agents.

## 6. Agent Output Standards

Every agent step must produce a structured trace record:

```python
{
    "agent_name": "Carbon Intelligence Agent",
    "step_id": "carbon-001",
    "input_summary": "Optimized route O01 with EV_VAN_05",
    "tool_or_function_used": "calculate_ev_co2e",
    "output_summary": "5.51 kWh, 3.91 kgCO2e",
    "decision_rationale": "EV route has lower emissions for compact route.",
    "status": "completed"
}
```

Rules:

- Agents should call deterministic tools for math and validation.
- Agent outputs must be JSON-serializable.
- Each run must save trace output for the dashboard.
- Trace should be readable by judges without inspecting code.

## 7. Plan Storage Standards

Use local file-based storage for the hackathon.

Each optimization run should write:

```text
outputs/
  runs/
    <run_id>/
      run_metadata.json
      agent_trace.json
      baseline_plan.json
      candidate_plans.json
      optimized_plan.json
      constraint_results.json
      metrics_summary.json
      disruption_event.json
      reoptimized_plan.json
      approval_audit.json
      decision_summary.json
```

Rules:

- Use a timestamp or UUID for `run_id`.
- Store generated run files under `outputs/runs`, not inside `data`.
- `data/greendispatch-ai-dataset` is source demo data and should remain stable.
- User-edited scenarios belong under `data/user-edited-scenarios/*.json`.
- Dashboard should read the latest run or selected run from `outputs/runs`.
- Approval decisions must be stored in `approval_audit.json`.

Recommended module:

```text
src/core/plan_store.py
```

Use a separate module for user-edited scenario inputs:

```text
src/core/scenario_store.py
```

`scenario_store.py` should save and load JSON scenario input files from `data/user-edited-scenarios` without overwriting the source dataset.

Required functions:

- `create_run_id()`
- `save_run_artifact(run_id, name, payload)`
- `load_run_artifact(run_id, name)`
- `list_runs()`
- `load_latest_run()`

## 8. Code Review Checklist

Review every pull request or change against this checklist.

### 8.1 Requirements

- [ ] Change maps to a spec increment or requirement ID.
- [ ] Hackathon non-negotiables are preserved.
- [ ] No customer, confidential, personal, or client-branded data is introduced.
- [ ] Baseline and assumptions are visible for sustainability claims.

### 8.2 Python

- [ ] Core logic is outside Streamlit rendering code.
- [ ] Functions are typed where practical.
- [ ] Calculations are deterministic.
- [ ] Required tests were added or updated.
- [ ] Missing-data and invalid-input cases are handled.
- [ ] Paths use `pathlib.Path`.

### 8.3 Streamlit

- [ ] Dashboard remains the first usable screen.
- [ ] UI supports the demo flow in 3 to 5 minutes.
- [ ] Input widgets are validated before running optimization.
- [ ] Session state is used intentionally.
- [ ] Styling is centralized and not excessive.
- [ ] Tables and KPIs are readable.

### 8.4 Agents

- [ ] Agent output is structured and JSON-serializable.
- [ ] Trace fields are complete.
- [ ] Agents use deterministic tools for math.
- [ ] Constraint failures are visible.
- [ ] Human approval remains mandatory.

### 8.5 Storage

- [ ] Source dataset is not overwritten by generated runs.
- [ ] Run artifacts are stored under `outputs/runs/<run_id>`.
- [ ] Approval audit is stored.
- [ ] Dashboard can reload the latest run.

### 8.6 Documentation

- [ ] README/setup instructions remain accurate.
- [ ] Open-source components are declared.
- [ ] Known limitations are updated.
- [ ] Architecture or assumptions docs are updated if behavior changed.

## 9. Definition Of Review Approval

A change is review-ready when:

- It runs locally.
- It has tests for calculation or constraint changes.
- It keeps the dashboard demoable.
- It preserves synthetic-data safety.
- It supports at least one spec increment.
- It improves or preserves the final hackathon story.
