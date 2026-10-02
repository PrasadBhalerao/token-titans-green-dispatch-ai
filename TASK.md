# GreenDispatch AI Task Plan

Action backlog for building the GreenDispatch AI hackathon prototype.

Primary references:

- `INSTRUCTIONS.md`
- `docs/greendispatch-ai-spec.md`
- `docs/greendispatch-ai-implementation-plan.md`
- `docs/python-streamlit-code-guidelines.md`
- `data/greendispatch-ai-dataset/README.md`

## Build Principles

- Build incrementally and keep every increment demoable.
- Use Python + Streamlit + pandas + Plotly + pytest.
- Keep deterministic calculations in `src/core`.
- Keep agent workflow and trace logic in `src/agents`.
- Keep Streamlit rendering in `src/ui`.
- Store generated run artifacts under `outputs/runs/<run_id>/`.
- Never overwrite source demo data in `data/greendispatch-ai-dataset`.
- Use only public, open, or synthetic data.
- Show assumptions beside every sustainability impact claim.
- Keep human approval mandatory before finalizing the optimized recommendation.

## Milestone 0: Project Setup

- [x] Create `requirements.txt`.
- [x] Create `app.py`.
- [x] Create `src/__init__.py`.
- [x] Create `src/core/__init__.py`.
- [x] Create `src/agents/__init__.py`.
- [x] Create `src/ui/__init__.py`.
- [x] Create `outputs/runs/README.md`.
- [x] Add README run command for Streamlit.

Acceptance:

- [ ] `streamlit run app.py` starts the app.
- [x] Tests can run with `python -m unittest discover -s tests -v`; `pytest` is listed in `requirements.txt`.

## INC-01: Project Bootstrap And Data Loading

Goal: Load the synthetic dataset and validate the data contract.

Tasks:

- [x] Implement `src/core/data_loader.py`.
- [x] Load required CSV files from `data/greendispatch-ai-dataset`.
- [x] Load `scenarios.json`.
- [x] Validate required files exist.
- [x] Validate required columns exist.
- [x] Display dataset row counts in the app.
- [x] Show synthetic-data notice in the UI.
- [x] Add `tests/test_data_loading.py`.

Acceptance:

- [x] Jobs, vehicles, routes, legs, assignments, metrics, and disruption data load successfully.
- [x] App shows row counts or preview tables.
- [x] Missing required file or column produces a readable error.

## INC-02: Calculation Core

Goal: Implement deterministic metric and emissions calculations.

Tasks:

- [x] Implement `src/core/emissions.py`.
- [x] Implement `src/core/metrics.py`.
- [x] Implement fuel calculation.
- [x] Implement EV energy calculation.
- [x] Implement idle fuel/energy calculation.
- [x] Implement CO2e calculation.
- [x] Implement capacity utilization calculation.
- [x] Implement baseline vs optimized reduction calculation.
- [x] Add `tests/test_emissions.py`.
- [x] Add `tests/test_metrics.py`.

Acceptance:

- [x] Calculated scenario totals match `metrics_by_scenario.csv` within rounding tolerance.
- [x] Calculated comparison values match `metrics_comparison.csv`.
- [x] Headline metrics reproduce the dataset values:
  - [x] Trips: 6 baseline, 4 optimized.
  - [x] Distance reduction: 53.6 km / 28.1%.
  - [x] Fuel reduction: 8.18 L / 35.1%.
  - [x] CO2e reduction: 18.5 kg / 29.8%.
  - [x] Idle reduction: 74 min / 65.5%.

## INC-03: Baseline Dispatch View

Goal: Show the manual/current dispatch plan.

Tasks:

- [x] Implement baseline route table.
- [x] Implement baseline job assignment table.
- [x] Implement baseline KPI cards.
- [x] Add baseline assumptions panel.
- [x] Add baseline metric validation in tests.

Acceptance:

- [x] User can view all 6 baseline routes.
- [x] User can see jobs assigned to each baseline route.
- [x] Baseline KPIs include trips, distance, fuel, CO2e, idle time, SLA adherence, utilization, and operating cost index.
- [x] Baseline assumptions are visible next to metrics.

## INC-04: Optimized Dispatch View

Goal: Show optimized dispatch and before/after impact.

Tasks:

- [x] Implement optimized route table.
- [x] Implement optimized job assignment table.
- [x] Implement baseline vs optimized KPI comparison.
- [x] Implement KPI delta panel.
- [x] Add Plotly comparison chart.
- [x] Show assumptions beside sustainability metrics.

Acceptance:

- [x] User can view all 4 optimized routes.
- [x] Dashboard shows baseline and optimized values side by side.
- [x] Dashboard highlights reductions in trips, distance, fuel, CO2e, idle time, planning time, and operating cost index.
- [x] CO2e reduction shows 18.5 kg / 29.8% for the supplied dataset.

## INC-05: Constraint Validation

Goal: Validate route feasibility and show failures clearly.

Tasks:

- [x] Implement `src/core/constraints.py`.
- [x] Validate vehicle capacity.
- [x] Validate SLA/time windows.
- [x] Validate vehicle availability.
- [x] Validate priority handling.
- [x] Render constraint results table.
- [x] Add `tests/test_constraints.py`.

Acceptance:

- [x] Each route receives a constraint status.
- [x] Invalid routes show explicit failure reasons.
- [x] Supplied routes pass expected validation.
- [x] Tests include at least one invalid capacity case.
- [x] Tests include at least one invalid SLA case.

## INC-06: Agent Workflow Trace

Goal: Demonstrate agentic orchestration.

Tasks:

- [x] Implement `src/agents/orchestrator.py`.
- [x] Implement `src/agents/forecasting_agent.py`.
- [x] Implement `src/agents/carbon_agent.py`.
- [x] Implement `src/agents/optimization_agent.py`.
- [x] Implement `src/agents/constraint_agent.py`.
- [x] Implement `src/agents/monitoring_agent.py`.
- [x] Define common trace record shape.
- [x] Render agent trace panel.
- [x] Add `tests/test_agent_trace.py`.

Acceptance:

- [x] Trace includes Orchestrator Agent.
- [x] Trace includes Forecasting Agent.
- [x] Trace includes Carbon Intelligence Agent.
- [x] Trace includes Optimization Agent.
- [x] Trace includes Constraint Agent.
- [x] Trace includes Monitoring Agent.
- [x] Each trace row includes agent name, step ID, input summary, tool/function used, output summary, rationale, and status.
- [x] Trace shows deterministic calculators used for math.

## INC-07: Human Approval Workflow

Goal: Keep human approval mandatory.

Tasks:

- [x] Add optimized-plan status field.
- [x] Default optimized plan status to `needs_human_review`.
- [x] Add Streamlit approval controls.
- [x] Add approve action.
- [x] Add reject action.
- [x] Add request-revision action.
- [x] Store approval decision in audit data.
- [x] Display approval status in dashboard.

Acceptance:

- [x] Optimized plan starts as `needs_human_review`.
- [x] User can approve, reject, or request revision.
- [x] Decision is recorded with timestamp/status.
- [x] UI states that agents recommend and humans approve.

## INC-08: Disruption And Re-Optimization

Goal: Demonstrate dynamic replanning.

Tasks:

- [x] Load disruption event from `disruption_events.csv`.
- [x] Add "Trigger disruption" dashboard action.
- [x] Display disruption details.
- [x] Load or generate reoptimized plan.
- [x] Compare optimized vs reoptimized metrics.
- [x] Update Monitoring Agent trace.
- [x] Validate reoptimized plan with Constraint Agent.

Acceptance:

- [x] User can trigger the supplied disruption.
- [x] App displays reoptimized routes.
- [x] Monitoring Agent explains why reoptimization occurred.
- [x] Constraint Agent validates reoptimized plan.
- [x] Dashboard shows metric changes after disruption.

## INC-09: Agent Sustainability Panel

Goal: Show the agent earns its keep.

Tasks:

- [x] Define agent sustainability metric schema.
- [x] Track or simulate model-call count.
- [x] Track or estimate token usage.
- [x] Track tool-call count.
- [x] Track retry count.
- [x] Track deterministic calculator usage.
- [x] Track cache/reused calculation count.
- [x] Calculate optimization gain per model call.
- [x] Render agent sustainability panel.

Acceptance:

- [x] Dashboard shows model calls, OpenAI token usage, tool calls, retries, deterministic calculator usage, and fallback status.
- [x] Dashboard explains why deterministic calculators reduce unnecessary model work.
- [x] Agent sustainability metrics appear beside the sustainability outcome.

## INC-10: Decision Summary Export Or Display

Goal: Deliver results where the dispatch decision is made.

Tasks:

- [x] Implement decision summary generator.
- [x] Include baseline values.
- [x] Include optimized values.
- [x] Include reductions.
- [x] Include assumptions.
- [x] Include agent recommendation.
- [x] Include approval status.
- [x] Render decision summary panel.
- [x] Persist `decision_summary.json`.

Acceptance:

- [x] Summary includes CO2e avoided.
- [x] Summary includes distance avoided.
- [x] Summary includes fuel saved.
- [x] Summary includes approval status.
- [x] Summary is suitable for final demo screenshot.

## INC-11: Documentation And Submission Artifacts

Goal: Prepare hackathon submission assets.

Tasks:

- [x] Update project README with setup and run instructions.
- [x] Add data-safety statement.
- [x] Add open-source component declaration.
- [x] Add known limitations.
- [x] Create `docs/agent-design.md`.
- [x] Create `docs/assumptions.md`.
- [x] Create `docs/architecture-diagram.mmd`.
- [x] Create `docs/architecture-diagram.png`.
- [x] Create `submission/README.md`.
- [x] Create `submission/pitch-deck-outline.md`.
- [x] Create `submission/demo-storyboard.md`.
- [x] Ensure demo video plan shows the agent running, not just slides.
- [x] Decide whether architecture diagram should be Mermaid source, PNG, or both. Decision: Mermaid source is canonical; PNG rendering is maintained for design review and submission visuals.
- [x] Decide whether user-edited scenarios are saved as new scenario files or only run metadata. Decision: store edited scenarios as JSON files under `data/user-edited-scenarios/`.
- [x] Decide whether OR-Tools is required for the first demo. Decision: defer Google OR-Tools until the heuristic optimizer is demo-ready and only add it if time remains.
- [x] Decide where pitch deck and storyboard live. Decision: keep final submission assets under `submission/`.

Acceptance:

- [x] README supports judge self-run.
- [x] Agent design document covers goal, users, data sources, tools, orchestration, decision points, human oversight, failure handling, privacy, auditability, and agent sustainability controls.
- [x] Architecture diagram includes user, scenario input, orchestrator, specialized agents, deterministic tools, synthetic data store, human approval gate, dashboard, and audit trail.
- [x] Pitch deck outline under `submission/` has 8 to 10 slides.
- [x] Demo storyboard under `submission/` fits 3 to 5 minutes.

## Cross-Cutting Tasks

### Plan Storage

- [x] Implement `src/core/plan_store.py`.
- [x] Implement `src/core/scenario_store.py`.
- [x] Implement `create_run_id()`.
- [x] Implement `save_run_artifact(run_id, name, payload)`.
- [x] Implement `load_run_artifact(run_id, name)`.
- [x] Implement `list_runs()`.
- [x] Implement `load_latest_run()`.
- [x] Save `run_metadata.json`.
- [x] Save `agent_trace.json`.
- [x] Save `baseline_plan.json`.
- [x] Save `candidate_plans.json`.
- [x] Save `optimized_plan.json`.
- [x] Save `constraint_results.json`.
- [x] Save `metrics_summary.json`.
- [x] Save `disruption_event.json`.
- [x] Save `reoptimized_plan.json`.
- [x] Save `approval_audit.json`.
- [x] Save `decision_summary.json`.
- [x] Save user-edited scenario inputs as JSON under `data/user-edited-scenarios/`.
- [x] Load selected user-edited scenario JSON files into the dashboard.

### Streamlit UX

- [x] Configure page title and wide layout.
- [x] Add sidebar scenario selector.
- [x] Add tabs for Baseline, Optimized, Agents, Disruption, Sustainability, Summary.
- [x] Add `st.data_editor` for editable jobs and vehicles.
- [x] Add forms for adding jobs or workload changes.
- [x] Add clear error handling with readable Streamlit messages.
- [x] Add restrained custom styling for KPI cards and status chips.

### Code Quality

- [x] Keep `app.py` thin.
- [x] Keep business logic out of Streamlit rendering functions.
- [x] Use `pathlib.Path`.
- [x] Add type hints to public functions.
- [x] Keep agent outputs JSON-serializable.
- [x] Run tests before demo.
- [x] Review code against `docs/python-streamlit-code-guidelines.md`.

## Demo Readiness Checklist

- [ ] App starts with `streamlit run app.py` after installing `requirements.txt`.
- [x] Synthetic dataset loads.
- [x] Baseline plan visible.
- [x] Optimized plan visible.
- [x] Before/after metrics visible.
- [x] Assumptions visible beside impact claims.
- [x] Agent trace visible.
- [x] Human approval visible.
- [x] Disruption and reoptimization visible.
- [x] Agent sustainability visible.
- [x] Decision summary visible.
- [x] README and docs ready.
- [x] No customer, confidential, personal, or client-branded data present.
