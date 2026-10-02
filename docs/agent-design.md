# GreenDispatch AI Design Document

Agentic Carbon-Aware Scheduling & Dispatch Optimizer  
Team Token Titans

## 1. Purpose

This document describes the end-to-end design for GreenDispatch AI, including product flow, system architecture, agent responsibilities, data model, calculation methodology, Streamlit dashboard design, run storage, human approval, failure handling, testing, and hackathon artifact alignment.

Primary references:

- `docs/hackathon-details.md`
- `docs/greendispatch-ai-spec.md`
- `docs/greendispatch-ai-implementation-plan.md`
- `docs/python-streamlit-code-guidelines.md`
- `INSTRUCTIONS.md`
- `TASK.md`

## 2. Solution Goal

GreenDispatch AI helps dispatch planners compare a baseline dispatch plan against an agentic optimized plan, quantify sustainability and operational improvements, and approve the final recommendation with an auditable decision trail.

The prototype must demonstrate that agentic AI can:

- Understand dispatch demand, workload, vehicle constraints, and time windows.
- Calculate fuel, energy, idle, distance, cost-index, and CO2e metrics.
- Generate and explain a carbon-aware optimized dispatch plan.
- Validate recommendations against operational constraints.
- Re-plan when a disruption occurs.
- Show agent sustainability metrics to justify the compute footprint.

## 3. Users And Workflow

| User | Primary need | Design response |
| --- | --- | --- |
| Dispatch planner | Compare feasible dispatch options quickly | Baseline and optimized route views with approval controls |
| Fleet manager | Reduce trips, distance, fuel, idle time, and cost | Before/after KPI cards and route-level tables |
| Sustainability analyst | Quantify emissions impact with assumptions | CO2e formulas, factors, assumptions, and source notes |
| Operations leader | Approve decisions with trade-off visibility | Decision summary and approval audit |
| Hackathon judge | See agentic depth and measurable impact | Agent trace, disruption re-optimization, and demo-ready dashboard |

## 4. System Context

The hackathon version is a local Streamlit app using synthetic data.

```text
User / Planner
    |
    v
Streamlit Dashboard
    |
    +--> Data Loader
    +--> Calculation Core
    +--> Agent Orchestrator
    +--> Plan Store
    |
    v
Local Synthetic Dataset + Run Artifacts
```

No private customer systems, production dispatch systems, paid routing APIs, or external databases are required for the demo.

## 5. High-Level Architecture

```text
                                      +----------------------+
                                      |  Streamlit Dashboard |
                                      +----------+-----------+
                                                 |
                       +-------------------------+-------------------------+
                       |                         |                         |
                       v                         v                         v
              +----------------+        +----------------+        +----------------+
              |  Data Loader   |        |  Plan Store    |        | UI Components  |
              +-------+--------+        +--------+-------+        +--------+-------+
                      |                          |                         |
                      v                          v                         |
          +-----------------------+    +---------------------+              |
          | Synthetic CSV / JSON  |    | outputs/runs/<id>/ |              |
          +-----------------------+    +---------------------+              |
                                                                             |
                                                                             v
                  +-------------------------------------------------------------+
                  |                    Orchestrator Agent                       |
                  +------+------+------+------+---------------+----------------+
                         |      |      |      |               |
                         v      v      v      v               v
                  Forecast  Carbon  Optimize Constraint   Monitoring
                   Agent    Agent    Agent     Agent        Agent
                         \      |      |      /               |
                          \     |      |     /                |
                           v    v      v    v                 v
                        +------------------------+     +-------------------+
                        | Deterministic Tools    |     | Disruption Logic  |
                        | emissions, metrics,    |     | re-optimization   |
                        | constraints, scoring   |     +-------------------+
                        +-----------+------------+
                                    |
                                    v
                         +----------------------+
                         | Recommendation +     |
                         | Agent Trace + Audit  |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Human Approval Gate  |
                         +----------------------+
```

## 6. Selected Technology Stack

| Layer | Technology |
| --- | --- |
| UI | Streamlit |
| Language | Python |
| Data processing | pandas |
| Charts | Plotly |
| Tests | pytest |
| Optimization | Explainable Python heuristics first; OR-Tools optional |
| Agent orchestration | Lightweight custom orchestrator |
| Storage | Local CSV/JSON files |

Rationale:

- Streamlit is fast enough for a hackathon dashboard and supports forms, editable tables, tabs, buttons, status panels, and charting.
- Python keeps calculations, tests, and optimization logic simple.
- Local JSON run storage is easier than introducing a database.

## 7. Data Design

### 7.1 Source Dataset

The source demo dataset lives under:

```text
data/greendispatch-ai-dataset/
```

Required files:

| File | Purpose |
| --- | --- |
| `locations.csv` | Depot and stop locations |
| `jobs.csv` | Dispatch and service jobs |
| `vehicles.csv` | Vehicle capacity, fuel/energy, cost, and emission attributes |
| `distance_matrix.csv` | Distance and travel time between locations |
| `emission_factors.csv` | CO2e factors and source notes |
| `fuel_usage_profiles.csv` | Fuel/energy usage assumptions |
| `plan_routes.csv` | Baseline, optimized, and reoptimized route summaries |
| `plan_legs.csv` | Leg-level route distances and times |
| `plan_assignments.csv` | Job-to-route assignments |
| `metrics_by_scenario.csv` | Scenario-level totals |
| `metrics_comparison.csv` | Baseline vs optimized deltas |
| `disruption_events.csv` | Disruption event definition |
| `scenarios.json` | Scenario metadata and formulas |

### 7.2 Data Safety Rules

- Treat all included data as synthetic.
- Do not add customer, confidential, personal, or client-branded data.
- Do not overwrite source dataset files during optimization runs.
- Generated outputs must be stored under `outputs/runs/<run_id>/`.

### 7.3 User-Edited Scenario Storage

User-edited scenarios are stored as JSON files under:

```text
data/user-edited-scenarios/
```

This folder is for user-created or user-modified scenario inputs, not generated optimization outputs.

Recommended file naming:

```text
scenario_<timestamp_or_short_id>.json
```

Recommended module:

```text
src/core/scenario_store.py
```

Responsibilities:

- Save user-edited jobs, vehicles, locations, and optional distance overrides.
- Preserve a reference to the source scenario or source run.
- Include data-safety flags confirming synthetic data only.
- Include assumptions and change log entries.
- Load selected user-edited scenarios back into the dashboard.

Generated agent outputs, optimized plans, metrics, and approval decisions still belong under `outputs/runs/<run_id>/`.

## 8. Run Storage Design

Each optimization run gets a unique run ID.

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

Recommended module:

```text
src/core/plan_store.py
```

Responsibilities:

- Create run IDs.
- Save JSON-serializable outputs.
- Load selected run artifacts.
- Load latest run.
- Preserve approval audit history.
- Keep source data and generated outputs separate.

## 9. Agent Design

Each agent produces a structured trace record:

```json
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

### 9.1 Orchestrator Agent

Purpose:

- Owns the end-to-end workflow.
- Calls specialized agents.
- Collects trace records.
- Persists run artifacts.
- Prepares the final recommendation for human approval.

Inputs:

- Scenario data.
- User edits from dashboard.
- Baseline and optimized plan data.
- Disruption events.

Outputs:

- Agent trace.
- Candidate plans.
- Optimized recommendation.
- Metrics summary.
- Decision summary.

### 9.2 Forecasting Agent

Purpose:

- Summarizes job demand, workload, priorities, SLA pressure, and capacity needs.

Prototype behavior:

- Uses job counts, demand totals, priority distribution, and time windows from the synthetic dataset.
- Does not require external forecasting models.

Outputs:

- Workload summary.
- SLA-sensitive jobs.
- Priority pressure notes.

### 9.3 Carbon Intelligence Agent

Purpose:

- Calculates fuel, energy, idle impact, and CO2e.
- Explains emission assumptions and factors.

Tools:

- `calculate_fuel_liters`
- `calculate_energy_kwh`
- `calculate_co2e`
- `calculate_reductions`

Outputs:

- Route-level emissions.
- Scenario-level emissions.
- Baseline vs optimized CO2e avoided.

### 9.4 Optimization Agent

Purpose:

- Generates or replays candidate route plans.
- Scores alternatives by distance, emissions, cost index, utilization, SLA, and idle time.

Prototype behavior:

- Uses explainable heuristic optimization.
- Can replay the prepared optimized plan if live optimization is incomplete.
- Must label replayed/generated data clearly.

Outputs:

- Candidate plans.
- Recommended optimized plan.
- Rationale for recommendation.

### 9.5 Constraint Agent

Purpose:

- Validates route feasibility.

Checks:

- Capacity.
- SLA/time windows.
- Vehicle availability.
- Priority handling.
- Operational constraints.

Outputs:

- Constraint results.
- Failure reasons for invalid routes.
- Validation status for final recommendation.

### 9.6 Monitoring Agent

Purpose:

- Detects disruption and triggers re-optimization.

Prototype event:

- Vehicle unavailability from `disruption_events.csv`.

Outputs:

- Disruption analysis.
- Reoptimization trigger.
- Revised plan comparison.

## 10. Orchestration Sequence

### 10.1 Normal Optimization

```text
1. User loads scenario.
2. Data Loader validates dataset.
3. Orchestrator creates run ID.
4. Forecasting Agent summarizes workload.
5. Carbon Intelligence Agent calculates baseline impact.
6. Optimization Agent generates or loads optimized plan.
7. Constraint Agent validates optimized plan.
8. Carbon Intelligence Agent calculates optimized impact.
9. Orchestrator builds metrics summary and decision summary.
10. Dashboard displays results.
11. Human approves, rejects, or requests revision.
12. Plan Store persists run artifacts.
```

### 10.2 Disruption Re-Optimization

```text
1. User triggers disruption.
2. Monitoring Agent reads disruption event.
3. Orchestrator identifies affected routes and vehicles.
4. Optimization Agent produces reoptimized plan.
5. Constraint Agent validates reoptimized plan.
6. Carbon Intelligence Agent recalculates impact.
7. Dashboard compares optimized vs reoptimized plan.
8. Human reviews revised recommendation.
9. Plan Store persists disruption and reoptimized artifacts.
```

## 11. Deterministic Tools

Core calculation and validation should live under `src/core`.

Recommended modules:

| Module | Responsibility |
| --- | --- |
| `data_loader.py` | Read and validate CSV/JSON source data |
| `emissions.py` | Fuel, energy, idle, and CO2e calculations |
| `metrics.py` | Scenario totals, reductions, KPI formatting |
| `constraints.py` | Capacity, SLA, availability, and priority validation |
| `optimizer.py` | Explainable heuristic route optimization |
| `baseline.py` | Baseline plan assembly or replay |
| `plan_store.py` | Run artifact persistence |

Rules:

- Use Python for arithmetic and validation.
- Do not ask an LLM to calculate numeric totals.
- Keep deterministic functions unit-testable.

## 12. Measurement Methodology

Use these formulas unless a documented replacement is added:

```text
fuel_liters = distance_km * fuel_rate_l_per_100km / 100
idle_fuel_liters = idle_minutes * idle_fuel_l_per_hour / 60
fuel_vehicle_co2e_kg = (fuel_liters + idle_fuel_liters) * kgCO2e_per_liter

energy_kwh = distance_km * energy_rate_kwh_per_100km / 100
idle_energy_kwh = idle_minutes * idle_energy_kwh_per_hour / 60
ev_co2e_kg = (energy_kwh + idle_energy_kwh) * kgCO2e_per_kwh

absolute_reduction = baseline_value - optimized_value
reduction_pct = absolute_reduction / baseline_value * 100
```

Display expectations:

- Distance, fuel, energy, CO2e, and cost index: 2 decimals.
- Percentages: 1 decimal.
- Assumptions must appear beside sustainability claims.

## 13. Dashboard Design

### 13.1 Streamlit Layout

The first screen should be the operational dashboard, not a landing page.

Recommended tabs:

1. Overview
2. Baseline
3. Optimized
4. Agents
5. Disruption
6. Sustainability
7. Summary

Sidebar:

- Scenario selector.
- Run optimization button.
- Trigger disruption button.
- Latest run selector.

### 13.2 Dashboard Sections

Required sections:

- KPI cards for baseline vs optimized.
- Route plan table.
- Job assignment table.
- Emissions and assumptions panel.
- Agent trace panel.
- Human approval panel.
- Disruption and re-optimization panel.
- Agent sustainability panel.
- Decision summary panel.

### 13.3 User Inputs

Streamlit can support optional interactive input:

- `st.data_editor` for jobs and vehicles.
- `st.form` for adding a job.
- `st.selectbox` for destination, priority, scenario, vehicle.
- `st.number_input` for demand, volume, capacity, fuel/energy rates.
- `st.time_input` for ready and due times.
- `st.button` for optimization, disruption, approval, rejection, revision.

Prototype priority:

1. Load and replay supplied dataset.
2. Allow simple edits through `st.data_editor`.
3. Persist edited scenario as part of run metadata if edits are used.

## 14. Human Approval Design

Optimized plans start with:

```text
status = needs_human_review
```

Available actions:

- Approve.
- Reject.
- Request revision.

Audit record fields:

| Field | Description |
| --- | --- |
| `run_id` | Optimization run ID |
| `decision` | approve, reject, request_revision |
| `timestamp` | Decision timestamp |
| `decision_summary` | Short text shown to user |
| `reviewer_note` | Optional human note |

The dashboard must clearly state that agents recommend and humans approve.

## 15. Failure And Fallback Handling

| Failure | Handling |
| --- | --- |
| Missing dataset file | Stop run and show readable error |
| Missing required columns | Stop run and show file/column names |
| Invalid route capacity | Mark route invalid and show reason |
| SLA violation | Mark route warning or invalid based on rule |
| Optimization fails | Fall back to prepared optimized plan and label it clearly |
| Disruption reoptimization unavailable | Show disruption details and explain missing replan |
| Run artifact save fails | Show warning; keep in-memory result visible |

## 16. Privacy, Safety, And Auditability

Privacy and data safety:

- Use synthetic data only.
- No customer data.
- No personal data.
- No confidential data.
- No client branding.

Auditability:

- Persist agent trace.
- Persist constraint results.
- Persist metrics summary.
- Persist approval audit.
- Persist decision summary.

## 17. Agent Sustainability Design

The dashboard must show agent sustainability metrics:

| Metric | Meaning |
| --- | --- |
| Agent steps | Number of workflow steps performed |
| Model calls | Number of live LLM calls; zero when deterministic fallback is used |
| Token estimate | Estimated input/output tokens |
| Tool calls | Number of deterministic tool calls |
| Retry count | Number of rework attempts |
| Cache reuse | Reused calculations or loaded cached results |
| Deterministic calculator calls | Calculations performed outside the model |
| Optimization gain per model call | Sustainability benefit relative to agent effort |

Design principle:

- Use the LLM or agent reasoning for planning and explanation.
- Use deterministic Python for math, constraints, and metrics.

## 18. Testing Design

Minimum tests:

| Test file | Coverage |
| --- | --- |
| `tests/test_data_loading.py` | Required files and columns |
| `tests/test_emissions.py` | Fuel, energy, idle, CO2e formulas |
| `tests/test_metrics.py` | Scenario totals and reductions |
| `tests/test_constraints.py` | Valid and invalid route cases |
| `tests/test_agent_trace.py` | Required agent roles and trace fields |

Manual demo validation:

- App starts.
- Dataset loads.
- Baseline visible.
- Optimized visible.
- Agent trace visible.
- Human approval works.
- Disruption works.
- Agent sustainability visible.
- Decision summary visible.

## 19. Deployment And Run Assumptions

Hackathon local run:

```text
pip install -r requirements.txt
streamlit run app.py
```

No cloud deployment is required for the proof of concept.

Required documentation:

- Setup instructions.
- Run instructions.
- Known limitations.
- Open-source component declaration.
- Synthetic-data statement.

## 20. Design Decisions

| Decision | Rationale |
| --- | --- |
| Streamlit instead of React | Faster dashboard delivery and fewer integration points |
| Local JSON run storage instead of database | Sufficient for demo, easy to inspect |
| User-edited scenarios stored as JSON files | Keeps edited inputs versionable, inspectable, and separate from generated run outputs |
| Mermaid architecture diagram is canonical | Easy to edit in source control and render later as image if needed |
| Architecture PNG stored in `docs/architecture-diagram.png` | Gives the team a ready visual for design review, pitch deck, and demo walkthrough |
| Deterministic calculations in Python | Accuracy, testability, and auditability |
| Lightweight custom orchestrator | Easier to trace for judges |
| Heuristic optimizer first | Explainable, demo-safe, and avoids overbuilding |
| OR-Tools deferred until the heuristic optimizer is demo-ready | Google OR-Tools can improve routing later, but it is not required for the initial hackathon demo |
| Pitch deck and demo storyboard stored in `submission/` | Keeps final submission assets separate from engineering design documents |
| Prepared synthetic scenarios | Reliable 3 to 5 minute demo |

## 21. Resolved Follow-Ups

- OR-Tools means Google OR-Tools, an open-source optimization solver library commonly used for vehicle-routing and scheduling problems. For this project, keep the first optimizer heuristic and explainable; consider OR-Tools only after the heuristic optimizer is demo-ready and time remains.
- Pitch deck, demo storyboard, video script, and final submission visuals should live in `submission/`. Planning, spec, design, and engineering standards remain in `docs/`.

## 22. Design Completion Checklist

- [x] Goal documented.
- [x] Users and workflow documented.
- [x] Data sources documented.
- [x] Agent architecture documented.
- [x] Tools and deterministic functions documented.
- [x] Orchestration flow documented.
- [x] Decision points documented.
- [x] Human oversight documented.
- [x] Failure and fallback handling documented.
- [x] Privacy and auditability documented.
- [x] Agent sustainability documented.
- [x] Architecture diagram included as Mermaid source in `docs/architecture-diagram.mmd`.
- [x] Architecture diagram rendered as PNG in `docs/architecture-diagram.png`.
