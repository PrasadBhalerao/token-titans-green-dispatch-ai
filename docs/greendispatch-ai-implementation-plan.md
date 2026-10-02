# GreenDispatch AI Implementation Plan

Agentic Carbon-Aware Scheduling & Dispatch Optimizer  
Tagline: Optimize every dispatch for operations, cost, and carbon.

## 1. Executive Summary

GreenDispatch AI is a hackathon proof of concept for carbon-aware scheduling and dispatch optimization. It helps dispatch planners compare a baseline operational plan against an agentic optimized plan, showing measurable reductions in distance, fuel or energy use, CO2e emissions, trips, idle time, and manual planning effort.

The solution will demonstrate a multi-agent workflow where specialized agents forecast demand, estimate emissions, evaluate dispatch options, validate constraints, monitor disruption scenarios, and recommend optimized plans. A human approval step remains part of the workflow before high-impact decisions are finalized.

## 2. Hackathon Fit

GreenDispatch AI fits the suggested track of forecasting, scheduling, and dispatch, while also supporting carbon and ESG intelligence.

The solution aligns with the hackathon expectations as follows:

| Hackathon expectation | GreenDispatch AI response |
| --- | --- |
| Identify a sustainability problem | Inefficient dispatch planning causes avoidable kilometers, fuel use, emissions, idle time, and underutilized assets. |
| Build an agentic workflow | Orchestrator Agent coordinates forecasting, carbon intelligence, optimization, constraints, monitoring, and human approval. |
| Measure what changed | Dashboard compares baseline vs optimized plan using distance, trips, fuel, CO2e, utilization, idle time, and planning time. |
| Prove agent sustainability | Track model calls, token usage, retry counts, tool calls, cache hits, and compute-aware design choices. |
| Use safe data | Use only public, open, or synthetic dispatch, vehicle, location, and emissions-factor data. |

## 3. Target Users

- Dispatch planners who need to assign vehicles or field resources efficiently.
- Fleet managers who need better utilization and lower operating cost.
- Sustainability teams who need auditable emissions estimates.
- Operations leaders who need trade-off visibility before dispatch decisions.
- Field-service or logistics teams handling delivery, maintenance, or asset movement.

## 4. Problem Statement

Current dispatch workflows usually optimize for availability, cost, and time, while sustainability impact is handled later or not at all. This causes avoidable trips, longer routes, excessive idle time, higher fuel or energy consumption, and preventable CO2e emissions.

The problem appears frequently in logistics, field operations, transportation, retail distribution, utility maintenance, banking field services, insurance inspections, and any organization that sends people, vehicles, or assets across locations.

## 5. Solution Scope

The hackathon PoC will focus on a controlled synthetic dispatch scenario:

- 8 to 20 delivery or field-service jobs.
- 3 to 6 vehicles or mobile assets.
- Capacity, availability, location, operating cost, and emission-factor attributes.
- Distance or duration matrix between locations.
- SLA windows or priority levels.
- Baseline dispatch plan generated with simple first-fit or manual-style assignment.
- Agentic optimized plan generated through multi-step reasoning and optimization.
- Disruption simulation such as traffic delay, vehicle unavailability, or urgent new request.

Out of scope for the hackathon PoC:

- Live integration with customer systems.
- Real customer data.
- Production routing engine integration.
- Financially binding dispatch execution.
- Fully autonomous dispatch without human approval.

## 6. Success Criteria

The prototype should successfully demonstrate:

- A baseline dispatch plan.
- An optimized dispatch plan for the same work.
- Quantified sustainability and operational delta.
- At least one dynamic re-optimization scenario.
- Agent trace showing which agents acted, what data they used, and why the recommendation changed.
- Human approval gate before final plan acceptance.
- Agent sustainability metrics, including token/tool usage and retry discipline.

## 6.1 Spec-Driven Delivery Alignment

This implementation plan is governed by the spec-driven build contract in `docs/greendispatch-ai-spec.md`.

The spec provides:

- Requirement IDs for hackathon non-negotiables, functional requirements, and non-functional requirements.
- A data contract for the generated dataset.
- Calculation and rounding rules.
- Agent trace contract.
- Incremental build slices with acceptance criteria and test expectations.
- Definition of done for hackathon submission.

Use `docs/python-streamlit-code-guidelines.md` for Python, Streamlit, code review, and storage standards.

The build should progress incrementally from data loading to calculation core, baseline view, optimized view, constraint validation, agent trace, human approval, disruption re-optimization, agent sustainability, decision summary, and final artifacts.

## 7. Proposed Architecture

```text
User / Planner
    |
    v
Dispatch Scenario Input
    |
    v
Orchestrator Agent
    |
    +--> Forecasting Agent
    |       - estimates demand/load
    |       - identifies priority and SLA pressure
    |
    +--> Carbon Intelligence Agent
    |       - estimates fuel/energy use
    |       - calculates CO2e emissions
    |       - applies emission factors by vehicle type
    |
    +--> Optimization Agent
    |       - creates candidate schedules
    |       - consolidates trips
    |       - evaluates route and assignment alternatives
    |
    +--> Constraint Agent
    |       - validates capacity, SLA, availability, distance, cost, and priority constraints
    |
    +--> Monitoring Agent
            - compares planned vs actual
            - detects disruption
            - triggers re-optimization

    |
    v
Human Approval Step
    |
    v
Sustainability Dashboard + Audit Trail
```

## 7.1 Plan Storage And Run Artifacts

The source dataset remains under `data/greendispatch-ai-dataset`. Generated agent outputs and optimized plans must not overwrite source data.

Each optimization run should create a run folder:

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

The dashboard should read from the current in-memory run while the user is interacting, then persist structured outputs to `outputs/runs/<run_id>/` so the result can be inspected, replayed, and shown in the demo.

Recommended module:

```text
src/core/plan_store.py
```

Required responsibilities:

- Create stable run IDs.
- Save JSON-serializable run artifacts.
- Load latest or selected run.
- Preserve approval audit entries.
- Keep generated outputs separate from source demo data.

## 8. Agent Responsibilities

### 8.1 Orchestrator Agent

Responsibilities:

- Accept dispatch scenario input.
- Break the task into planning steps.
- Coordinate specialized agents.
- Request rework when constraints fail.
- Produce a final recommendation with rationale.
- Maintain an audit trail of agent decisions.

Inputs:

- Jobs, vehicles, constraints, emission factors, baseline assumptions.

Outputs:

- Agent plan, task trace, final recommendation, approval request.

### 8.2 Forecasting Agent

Responsibilities:

- Estimate operational load from job list.
- Identify peak pressure points.
- Flag high-priority or SLA-sensitive jobs.
- Support disruption scenario assessment.

Prototype simplification:

- Use synthetic demand data and simple priority logic rather than external forecasting models.

### 8.3 Carbon Intelligence Agent

Responsibilities:

- Estimate fuel or energy use by distance and vehicle type.
- Convert fuel or energy use to CO2e.
- Compare baseline and optimized carbon footprint.
- Explain assumptions and emission factors.

Prototype calculation examples:

- Diesel vehicle: liters = kilometers * liters_per_km.
- EV vehicle: kWh = kilometers * kWh_per_km.
- CO2e = activity_value * emission_factor.

### 8.4 Optimization Agent

Responsibilities:

- Generate candidate vehicle-job assignments.
- Consolidate trips where capacity and SLA allow.
- Reduce distance, empty kilometers, idle time, and emissions.
- Balance cost, time, emissions, and utilization.

Prototype approaches:

- Heuristic route assignment.
- Greedy consolidation.
- Lightweight local search.
- Optional Google OR-Tools solver only after the heuristic optimizer is demo-ready and time allows.

### 8.5 Constraint Agent

Responsibilities:

- Validate each candidate plan.
- Reject plans that violate vehicle capacity, availability, job time windows, SLA, or operational rules.
- Return specific failure reasons for re-planning.

### 8.6 Monitoring Agent

Responsibilities:

- Compare planned vs actual or changed conditions.
- Detect disruption such as traffic delay, new request, or vehicle unavailability.
- Ask the orchestrator to re-optimize.
- Report the delta between original optimized plan and revised plan.

## 9. Human Oversight

Human approval is mandatory before dispatch execution. In the prototype, this will be represented as a visible approval step:

- Review baseline and optimized plans.
- Review sustainability delta and operational trade-offs.
- Approve, reject, or request a revised recommendation.
- Record approval decision in the audit trail.

The agent may recommend and explain, but it must not finalize financially, legally, contractually, or reputationally significant actions without human approval.

## 10. Data Plan

Use only synthetic data generated for the hackathon.

### 10.1 Sample Data Entities

Jobs:

| Field | Description |
| --- | --- |
| job_id | Unique delivery or service request ID |
| origin | Starting location or depot |
| destination | Delivery or service location |
| demand_units | Load or service capacity required |
| priority | Normal, high, urgent |
| sla_window | Required delivery or service time window |
| service_time_minutes | Time spent at destination |

Vehicles:

| Field | Description |
| --- | --- |
| vehicle_id | Unique vehicle or asset ID |
| type | Diesel van, EV van, truck, bike, etc. |
| capacity_units | Maximum capacity |
| start_location | Depot or current location |
| availability_window | Available operating hours |
| cost_per_km | Approximate operating cost |
| fuel_or_energy_rate | Liters/km or kWh/km |
| emission_factor | CO2e factor |

Distance Matrix:

| Field | Description |
| --- | --- |
| from_location | Start location |
| to_location | End location |
| distance_km | Estimated distance |
| travel_time_minutes | Estimated duration |

Emission Factors:

| Field | Description |
| --- | --- |
| vehicle_type | Vehicle category |
| activity_unit | Liter, kWh, or km |
| factor_kg_co2e | Emission factor per unit |
| source | Synthetic, GHG Protocol-aligned, or public reference |

## 11. Measurement Methodology

### 11.1 Baseline

The baseline plan will simulate a typical manual or simple rule-based dispatch approach:

- Assign jobs in request order.
- Prefer first available vehicle.
- Minimize SLA misses, but ignore emissions.
- Allow more trips if that is operationally easy.

### 11.2 Optimized Plan

The optimized plan will:

- Consolidate compatible jobs.
- Prefer lower-emission vehicles where practical.
- Reduce total distance and empty kilometers.
- Respect capacity, priority, and SLA constraints.
- Trigger human review for trade-offs.

### 11.3 Metrics

| Metric | Formula or source |
| --- | --- |
| Trips avoided | Baseline trips - optimized trips |
| Kilometers avoided | Baseline km - optimized km |
| Fuel saved | Baseline liters - optimized liters |
| Energy saved | Baseline kWh - optimized kWh |
| CO2e avoided | Baseline kg CO2e - optimized kg CO2e |
| Utilization improvement | Optimized utilization - baseline utilization |
| Idle time reduction | Baseline idle minutes - optimized idle minutes |
| Planning time saved | Estimated manual planning time - agent planning time |
| SLA adherence | Jobs meeting SLA / total jobs |

### 11.4 Example Calculation

Baseline:

- 3 trips.
- 180 km.
- 0.09 liters/km diesel rate.
- 2.68 kg CO2e/liter emission factor.

Optimized:

- 2 trips.
- 135 km.
- Same vehicle type and factor.

Impact:

- 45 km avoided.
- 4.05 liters fuel avoided.
- 10.85 kg CO2e avoided.
- 33.3% fewer trips.
- 25% distance reduction.

## 12. Agent Sustainability Plan

The submission must show that the agent itself is efficient and responsible. GreenDispatch AI will report:

- Number of agent steps per optimization.
- Number of model calls.
- Actual OpenAI input/output token usage when live LLM mode runs, with zero actual LLM tokens reported during deterministic fallback.
- Number of tool calls.
- Retry count and retry reasons.
- Cache usage for unchanged distance/emission calculations.
- Small-model vs large-model selection strategy.
- Prompt length control and structured inputs.
- Deterministic calculation tools for emissions and metrics.
- Audit trail for decisions, assumptions, and approvals.

Efficiency choices:

- Use deterministic functions for math and validation.
- Use LLM reasoning for planning, explanation, trade-off analysis, and exception handling.
- Cache distance matrix, emission factors, and repeated scenario evaluations.
- Keep agent instructions short and role-specific.
- Use structured JSON between agents where possible.
- Limit re-optimization scope to impacted jobs after disruption.

## 13. Prototype Features

### Must Have

- Synthetic scenario input.
- Baseline plan generation.
- Agentic optimized plan generation.
- Carbon and operational impact calculation.
- Dashboard comparing baseline vs optimized plan.
- Agent trace and rationale.
- Constraint validation.
- Human approval step.
- Disruption scenario and re-optimization.
- README with setup, run instructions, sample data, and known limitations.

### Should Have

- Exportable results summary.
- Scenario selector with 2 to 3 sample cases.
- Simple architecture diagram in the design document.
- Visual before/after route or assignment table.
- Agent sustainability metrics panel.

### Could Have

- Map visualization.
- OR-Tools-based optimization after the heuristic optimizer is demo-ready.
- Electricity grid carbon-intensity awareness for EV charging scenarios.
- What-if slider for cost vs carbon trade-off.
- Downloadable audit report.

## 14. Selected Tech Stack

Use this stack for the hackathon prototype:

| Layer | Selection | Rationale |
| --- | --- | --- |
| UI dashboard | Streamlit | Fastest path to an interactive dashboard with tables, KPIs, forms, tabs, and approval controls. |
| Backend/app core | Python | Strong fit for deterministic calculations, pandas, tests, and optimization heuristics. |
| Data handling | pandas | Straightforward CSV/JSON loading and tabular transformations. |
| Visualization | Plotly | Good KPI and comparison charts inside Streamlit. |
| Testing | pytest | Lightweight unit tests for data loading, emissions, metrics, constraints, and trace shape. |
| Optimization | Explainable Python heuristics first; Google OR-Tools optional after demo-ready | Keeps the demo transparent and avoids overbuilding. |
| Agent orchestration | Lightweight custom orchestrator | Enough for a hackathon demo and easy to trace. |
| Storage | Local CSV/JSON files | No database required for the proof of concept. |

Do not introduce React, FastAPI, a database, or a paid routing API unless the spec is explicitly revised. Streamlit can support the required user inputs through `st.form`, `st.data_editor`, `st.selectbox`, `st.number_input`, `st.time_input`, and `st.button`.

## 15. Spec-Driven Implementation Workplan

The detailed implementation sequence follows `docs/greendispatch-ai-spec.md`.

### INC-01: Project Bootstrap And Data Loading

Deliverables:

- Runnable Streamlit shell.
- Dataset loader.
- Required-file and required-column validation.
- Row-count or table preview.

Acceptance gate:

- Local app starts.
- Source dataset loads without credentials.
- Synthetic-data statement is visible in README or UI.

### INC-02: Calculation Core

Deliverables:

- Fuel, energy, idle, CO2e, utilization, and reduction calculators.
- Tests for emissions and metrics.

Acceptance gate:

- Calculated totals match `metrics_by_scenario.csv`.
- Calculated deltas match `metrics_comparison.csv`.

### INC-03: Baseline Dispatch View

Deliverables:

- Baseline route table.
- Baseline job assignment table.
- Baseline KPI cards.
- Baseline assumptions panel.

Acceptance gate:

- Baseline route count and headline metrics match the dataset.

### INC-04: Optimized Dispatch View

Deliverables:

- Optimized route table.
- Optimized job assignment table.
- Baseline vs optimized comparison.
- KPI delta panel.

Acceptance gate:

- Optimized route count is visible.
- Reductions in trips, distance, fuel, CO2e, idle time, planning time, and cost index are visible.

### INC-05: Constraint Validation

Deliverables:

- Capacity validation.
- SLA/time validation.
- Vehicle availability validation.
- Constraint results table.

Acceptance gate:

- Valid routes pass.
- Invalid test routes return explicit failure reasons.
- Constraint Agent trace references validation output.

### INC-06: Agent Workflow Trace

Deliverables:

- Structured trace for Orchestrator, Forecasting, Carbon Intelligence, Optimization, Constraint, and Monitoring agents.
- JSON-serializable trace records.

Acceptance gate:

- Each trace record includes agent name, step ID, input summary, tool/function used, output summary, rationale, and status.

### INC-07: Human Approval Workflow

Deliverables:

- Approval panel.
- Approve, reject, and request revision controls.
- Approval audit artifact.

Acceptance gate:

- Optimized plan starts in `needs_human_review`.
- Human decision is stored in `approval_audit.json`.

### INC-08: Disruption And Re-Optimization

Deliverables:

- Disruption trigger from `disruption_events.csv`.
- Reoptimized plan view.
- Optimized vs reoptimized comparison.
- Monitoring Agent trace.

Acceptance gate:

- Dashboard shows how the disruption changes route assignments and metrics.

### INC-09: Agent Sustainability Panel

Deliverables:

- Model-call count.
- Token estimate.
- Tool-call count.
- Retry count.
- Cache/reused calculation count.
- Deterministic calculator count.
- Optimization gain per model call.

Acceptance gate:

- Agent sustainability metrics appear next to the sustainability outcome.

### INC-10: Decision Summary Export Or Display

Deliverables:

- Concise decision summary.
- Baseline, optimized, reduction, assumptions, recommendation, and approval status.

Acceptance gate:

- Summary is suitable for a demo screenshot and final judging narrative.

### INC-11: Documentation And Submission Artifacts

Deliverables:

- README.
- Agent design document.
- Assumptions document.
- Architecture diagram.
- Pitch deck outline.
- Demo video storyboard.
- Open-source declaration.
- Known limitations.

Acceptance gate:

- Documentation meets the checklist in `docs/greendispatch-ai-spec.md`.

## 16. Suggested Team Roles

For a team of up to 5:

| Role | Responsibilities |
| --- | --- |
| Product and sustainability lead | Problem framing, impact metrics, assumptions, pitch narrative |
| Agent workflow engineer | Orchestrator, agents, prompts, trace, human approval |
| Optimization engineer | Baseline, optimization, constraints, emissions calculations |
| Frontend/dashboard engineer | Dashboard, comparison view, demo flow |
| Documentation and demo lead | README, design doc, pitch deck, demo video |

If fewer people are available, combine product with documentation, and combine optimization with agent workflow.

## 17. Repository Structure

```text
Sustainability Hackathon - Team Token Titans/
  README.md
  INSTRUCTIONS.md
  app.py
  requirements.txt
  data/
    greendispatch-ai-dataset/
      jobs.csv
      vehicles.csv
      locations.csv
      distance_matrix.csv
      emission_factors.csv
      fuel_usage_profiles.csv
      plan_routes.csv
      plan_legs.csv
      plan_assignments.csv
      metrics_by_scenario.csv
      metrics_comparison.csv
      disruption_events.csv
      scenarios.json
    user-edited-scenarios/
      README.md
      scenario-template.json
  docs/
    hackathon-details.md
    greendispatch-ai-implementation-plan.md
    greendispatch-ai-spec.md
    python-streamlit-code-guidelines.md
    agent-design.md
    architecture-diagram.mmd
    architecture-diagram.png
    assumptions.md
  submission/
    README.md
    pitch-deck-outline.md
    demo-storyboard.md
  src/
    agents/
      orchestrator.py
      forecasting_agent.py
      carbon_agent.py
      optimization_agent.py
      constraint_agent.py
      monitoring_agent.py
    core/
      baseline.py
      optimizer.py
      emissions.py
      constraints.py
      metrics.py
      plan_store.py
      data_loader.py
      scenario_store.py
    ui/
      dashboard.py
  tests/
    test_data_loading.py
    test_emissions.py
    test_constraints.py
    test_metrics.py
    test_agent_trace.py
  outputs/
    runs/
```

## 18. Required Hackathon Artifacts

### 18.1 Proof of Concept Repository

Must include:

- Working app or runnable notebook.
- README with setup instructions.
- Run instructions.
- Sample synthetic data.
- Known limitations.
- Declaration of any open-source components used.
- Statement that no customer, confidential, personal, or client-branded data is included.

README outline:

```text
# GreenDispatch AI

## What it does
## Why it matters
## Architecture
## Agent workflow
## Sample data
## How to run
## Demo scenario
## Sustainability methodology
## Agent sustainability metrics
## Known limitations
## Open-source components
```

### 18.2 Agent Design Document

Document path: `docs/agent-design.md`

Must include:

- Goal.
- Target users.
- Data sources.
- Agent architecture.
- Tools and deterministic functions.
- Orchestration flow.
- Decision points.
- Human oversight.
- Failure handling.
- Privacy and auditability.
- Agent sustainability controls.
- Architecture diagram.

Recommended sections:

```text
1. Solution goal
2. User and workflow
3. Data model
4. Agent architecture
5. Agent responsibilities
6. Orchestration sequence
7. Constraint validation
8. Human approval
9. Failure and fallback handling
10. Measurement methodology
11. Privacy and data safety
12. Agent sustainability
```

### 18.3 Architecture Diagram

Include at least:

- User/planner.
- Scenario input.
- Orchestrator Agent.
- Five specialized agents.
- Deterministic tools/calculators.
- Synthetic data store.
- Human approval gate.
- Dashboard and audit trail.

### 18.4 Pitch Deck

Submission path: `submission/pitch-deck-outline.md`

Eight to ten slide outline:

1. Title: GreenDispatch AI.
2. Problem: Dispatch planning creates avoidable emissions and inefficiency.
3. Users and pain: Dispatch planners, fleet managers, sustainability teams.
4. Solution: Multi-agent carbon-aware scheduling and dispatch optimizer.
5. How it works: Orchestrator plus specialized agents.
6. Demo scenario: Baseline vs optimized plan.
7. Measured impact: CO2e, km, fuel/energy, trips, utilization, time saved.
8. Agent sustainability: Token/tool efficiency, carbon-aware design, auditability.
9. Roadmap: Real integrations, route APIs, ERP/TMS/FSM integration, live monitoring.
10. Ask/close: Why this can scale and why now.

### 18.5 Demo Video

Storyboard path: `submission/demo-storyboard.md`

Target length: 3 to 5 minutes.

Storyboard:

1. Show problem scenario and synthetic dispatch requirements.
2. Generate baseline plan.
3. Show baseline distance, trips, fuel/energy, and CO2e.
4. Run GreenDispatch AI optimization.
5. Show agent trace and constraint validation.
6. Compare baseline vs optimized plan.
7. Show human approval step.
8. Trigger disruption scenario.
9. Show re-optimized plan.
10. Close with measured sustainability impact and agent sustainability metrics.

## 19. Demo Narrative

Suggested live demo script:

1. "We start with a normal dispatch workload: multiple jobs, limited vehicles, capacity constraints, and SLA windows."
2. "The baseline planner creates a workable plan, but it requires more trips and more kilometers."
3. "GreenDispatch AI asks specialized agents to evaluate demand, carbon impact, constraints, and alternative assignments."
4. "The optimized plan consolidates trips and selects lower-emission options where possible while preserving SLA adherence."
5. "The dashboard shows the operational and sustainability delta."
6. "A human planner reviews the recommendation before approval."
7. "Now we simulate a disruption: one vehicle becomes unavailable or an urgent job arrives."
8. "The Monitoring Agent triggers re-optimization and the system proposes a revised plan with a fresh impact calculation."

## 20. Risk and Mitigation

| Risk | Mitigation |
| --- | --- |
| Optimization becomes too complex | Start with heuristic optimization; add Google OR-Tools only after the heuristic optimizer is demo-ready and time permits. |
| Emissions assumptions are challenged | Clearly document formulas, factors, and synthetic assumptions. |
| Agent workflow looks like a single prompt | Show multi-agent trace, retries, validation, and re-planning. |
| Demo takes too long | Prepare fixed sample scenarios and cached outputs. |
| Dashboard overwhelms judges | Lead with 5 key KPIs and keep details expandable. |
| Data privacy concerns | Use only synthetic data and explicitly state this in README and deck. |

## 21. Judging Criteria Mapping

| Judging criterion | Evidence to show |
| --- | --- |
| Sustainability Impact & Measurability | Before/after CO2e, km, trips, fuel/energy, utilization, and assumptions. |
| Agentic Depth & Technical Implementation | Orchestrator, specialized agents, tools, trace, constraints, monitoring, re-optimization. |
| Sustainability of the Agent Itself | Token/tool metrics, retries, caching, deterministic calculators, scoped re-optimization. |
| Demo & Communication | Working app, clear narrative, dashboard, demo video. |
| Innovation & Creativity | Carbon-aware dispatch with dynamic re-planning and auditable sustainability value. |

## 22. Final Submission Checklist

- [ ] Working proof of concept runs locally.
- [ ] Synthetic data included.
- [ ] Spec file maintained in `docs/greendispatch-ai-spec.md`.
- [ ] Python and Streamlit guidelines maintained in `docs/python-streamlit-code-guidelines.md`.
- [ ] README includes setup, run instructions, sample data, and known limitations.
- [ ] Architecture diagram included.
- [ ] Mermaid architecture diagram maintained in `docs/architecture-diagram.mmd`.
- [ ] Architecture diagram PNG maintained in `docs/architecture-diagram.png`.
- [ ] Agent design document completed.
- [ ] Pitch deck completed with 8 to 10 slides under `submission/`.
- [ ] Demo storyboard completed under `submission/`.
- [ ] Demo video recorded, 3 to 5 minutes.
- [ ] Baseline vs optimized metrics included.
- [ ] CO2e methodology and assumptions documented.
- [ ] Agent sustainability metrics included.
- [ ] Human approval step demonstrated.
- [ ] Agent outputs, plan outputs, and approval audit stored under `outputs/runs/<run_id>/`.
- [ ] User-edited scenarios stored as JSON files under `data/user-edited-scenarios/`.
- [ ] Disruption and re-optimization demonstrated.
- [ ] Open-source components declared.
- [ ] No customer, confidential, personal, or client-branded data included.

## 23. Recommended Build Order

Build in this order to maximize demo readiness:

1. INC-01: Project bootstrap and data loading.
2. INC-02: Calculation core.
3. INC-03: Baseline dispatch view.
4. INC-04: Optimized dispatch view.
5. INC-05: Constraint validation.
6. INC-06: Agent workflow trace.
7. INC-07: Human approval workflow.
8. INC-08: Disruption and re-optimization.
9. INC-09: Agent sustainability panel.
10. INC-10: Decision summary export or display.
11. INC-11: Documentation and submission artifacts.

This order ensures that even if advanced optimization is not completed, the team still has a demonstrable sustainability workflow with measurable impact, a traceable agent story, and enough documentation for hackathon submission.
