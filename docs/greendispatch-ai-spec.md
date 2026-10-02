# GreenDispatch AI Specification

Spec-driven development plan for Team Token Titans  
Solution: GreenDispatch AI - Agentic Carbon-Aware Scheduling & Dispatch Optimizer  
Tagline: Optimize every dispatch for operations, cost, and carbon.

## 1. Spec Status

| Field | Value |
| --- | --- |
| Status | Draft for incremental build |
| Owner | Team Token Titans |
| Primary app goal | Demonstrate a working agentic carbon-aware dispatch optimizer |
| Primary demo data | `data/greendispatch-ai-dataset` |
| Primary UI | Dispatch optimization dashboard |
| Source precedence | Hackathon brief first, implementation plan second, dataset README third |

## 2. Source Documents

This spec is derived from:

- `INSTRUCTIONS.md`
- `docs/hackathon-details.md`
- `docs/greendispatch-ai-implementation-plan.md`
- `data/greendispatch-ai-dataset/README.md`
- `data/greendispatch-ai-dataset/metrics_comparison.csv`

If this spec conflicts with `docs/hackathon-details.md`, the hackathon brief wins.

## 3. Product Vision

GreenDispatch AI helps dispatch planners compare a manual baseline dispatch plan against an agentic optimized dispatch plan, then quantify operational and sustainability impact before a human approves the recommendation.

The prototype must show that agentic AI can:

- Understand dispatch demand and constraints.
- Calculate carbon and operational impact.
- Generate improved dispatch plans.
- Validate plans against constraints.
- React to disruptions.
- Explain decisions through an audit trail.
- Justify its own compute footprint.

## 4. Problem Statement

Fleet, logistics, field-service, and mobile-asset operations often optimize dispatch around availability, cost, and delivery time while treating sustainability as an after-the-fact report. This causes avoidable trips, longer distances, unnecessary idle time, poor asset utilization, higher fuel or energy use, and preventable CO2e emissions.

GreenDispatch AI addresses this by making carbon-aware optimization part of the dispatch decision itself.

## 5. Target Users

| User | Need |
| --- | --- |
| Dispatch planner | Create feasible plans quickly and compare alternatives. |
| Fleet manager | Reduce distance, trips, idle time, and cost. |
| Sustainability analyst | Quantify CO2e impact with documented assumptions. |
| Operations leader | Understand trade-offs before approving decisions. |
| Hackathon judge | See a working agentic workflow with measurable impact. |

## 6. Non-Negotiable Requirements

| ID | Requirement |
| --- | --- |
| HN-01 | Use only public, open, or synthetic data. |
| HN-02 | Do not use customer code, customer data, confidential data, personal data, or client branding. |
| HN-03 | State baseline and assumptions beside each sustainability impact claim. |
| HN-04 | Include human approval before the optimized recommendation is considered final. |
| HN-05 | Show genuine agentic behavior: planning, tool use, orchestration, traceability, error handling, feedback, and re-planning. |
| HN-06 | Show agent sustainability metrics: model calls, token usage, tool calls, retries, deterministic calculator usage, fallback status, and cache reuse. |
| HN-07 | Declare open-source components and pre-existing work. |
| HN-08 | Keep the demo runnable without private external systems. |
| HN-09 | Demo video must show the agent running, not only slides. |

## 7. Scope

### 7.1 In Scope

- Synthetic dispatch jobs, vehicles, locations, distance matrix, emission factors, and route plans.
- Baseline dispatch plan display.
- Optimized dispatch plan display.
- Baseline vs optimized KPI comparison.
- Fuel, energy, idle, distance, cost-index, and CO2e calculations.
- Agentic workflow trace.
- Constraint validation.
- Human approval workflow.
- Disruption and re-optimization scenario.
- Agent sustainability panel.
- Documentation and submission artifacts.

### 7.2 Out Of Scope

- Live integration with customer systems.
- Real fleet/customer data.
- Autonomous production dispatch.
- Paid map/routing API dependency as a required demo step.
- Financially, legally, contractually, or reputationally binding actions.

## 8. Baseline Demo Targets

The existing dataset provides these headline demo numbers:

| Metric | Baseline | Optimized | Reduction |
| --- | ---: | ---: | ---: |
| Trips | 6 | 4 | 33.3% |
| Distance | 190.82 km | 137.22 km | 28.1% |
| Fuel | 23.31 L | 15.13 L | 35.1% |
| CO2e | 62.14 kg | 43.64 kg | 29.8% |
| Idle time | 113 min | 39 min | 65.5% |
| Planning time | 90 min | 14 min | 84.4% |
| Operating cost index | 4766.62 | 3489.23 | 26.8% |

The implementation must be able to reproduce or explain these values from the dataset and formulas.

## 9. Functional Requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-01 | Load scenario data from local CSV/JSON files. | Must |
| FR-02 | Show baseline dispatch plan. | Must |
| FR-03 | Calculate baseline route metrics. | Must |
| FR-04 | Show optimized dispatch plan. | Must |
| FR-05 | Calculate optimized route metrics. | Must |
| FR-06 | Compare baseline vs optimized metrics. | Must |
| FR-07 | Show emissions and fuel/energy assumptions. | Must |
| FR-08 | Show agent workflow trace. | Must |
| FR-09 | Validate capacity, SLA, availability, priority, and operational constraints. | Must |
| FR-10 | Include human approval, rejection, or revision request. | Must |
| FR-11 | Trigger disruption scenario. | Must |
| FR-12 | Show re-optimized plan after disruption. | Must |
| FR-13 | Show agent sustainability metrics. | Must |
| FR-14 | Export or display concise decision summary. | Should |
| FR-15 | Provide architecture and assumptions documentation. | Must |
| FR-16 | Provide setup and run instructions. | Must |

## 10. Non-Functional Requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| NFR-01 | App must run locally using documented commands. | Must |
| NFR-02 | App must not require private credentials for demo. | Must |
| NFR-03 | Calculations must be deterministic and testable. | Must |
| NFR-04 | UI must be clear enough for a 3 to 5 minute demo. | Must |
| NFR-05 | Errors must be readable and actionable. | Should |
| NFR-06 | Agent prompts and outputs must be traceable. | Must |
| NFR-07 | Repeated calculations should be cached or reused where practical. | Should |
| NFR-08 | README must disclose synthetic data and limitations. | Must |

## 11. Data Contract

### 11.1 Required Dataset Files

| File | Purpose |
| --- | --- |
| `locations.csv` | Depot and destination locations. |
| `jobs.csv` | Dispatch/service jobs with demand, priority, and time windows. |
| `vehicles.csv` | Fleet capacity, fuel/energy rates, idle rates, emission factors, and cost index. |
| `distance_matrix.csv` | Distance and travel time between locations. |
| `emission_factors.csv` | CO2e factors and source notes. |
| `fuel_usage_profiles.csv` | Realistic fuel/energy usage assumptions. |
| `plan_routes.csv` | Baseline, optimized, and reoptimized route summaries. |
| `plan_legs.csv` | Leg-level route distances and travel times. |
| `plan_assignments.csv` | Job-to-route mapping. |
| `metrics_by_scenario.csv` | Scenario-level totals. |
| `metrics_comparison.csv` | Baseline vs optimized deltas. |
| `disruption_events.csv` | Disruption trigger and reoptimization context. |
| `scenarios.json` | Scenario metadata and formulas. |

### 11.2 User-Edited Scenario Files

User-edited scenarios must be stored as JSON files under:

```text
data/user-edited-scenarios/
```

Use `data/user-edited-scenarios/scenario-template.json` as the starter schema.

### 11.3 Data Rules

- Treat all provided data as synthetic demo data.
- Do not add private fleet, customer, employee, or client data.
- If new records are added, keep route IDs, vehicle IDs, job IDs, and scenario IDs stable and readable.
- If fuel or emission assumptions change, update `emission_factors.csv`, `fuel_usage_profiles.csv`, and documentation.
- Store user-edited scenario inputs in JSON files under `data/user-edited-scenarios`.
- Store generated optimization outputs under `outputs/runs/<run_id>`, not in `data/user-edited-scenarios`.

## 12. Calculation Rules

Use deterministic functions for all numeric metrics.

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

Rounding:

- Display distance, fuel, energy, CO2e, and cost index to 2 decimal places.
- Display percentages to 1 decimal place.
- Tests may allow small rounding tolerance.

## 13. Agent Contract

Each agent must expose or simulate a trace record with:

| Field | Description |
| --- | --- |
| `agent_name` | Agent role name. |
| `step_id` | Stable trace step ID. |
| `input_summary` | Data or context consumed. |
| `tool_or_function_used` | Deterministic tool, calculator, or workflow action. |
| `output_summary` | What the agent produced. |
| `decision_rationale` | Why the result matters. |
| `status` | `completed`, `warning`, `rejected`, or `needs_human_review`. |

Required agent roles:

- Orchestrator Agent.
- Forecasting Agent.
- Carbon Intelligence Agent.
- Optimization Agent.
- Constraint Agent.
- Monitoring Agent.

## 14. Incremental Build Plan

Each increment must be independently reviewable. Do not move to polish until the current increment can be demonstrated or tested.

### INC-01: Project Bootstrap And Data Loading

Goal: Establish the runnable project shell and load local synthetic data.

Scope:

- Create app entry point.
- Create package folders under `src`.
- Load CSV/JSON files from `data/greendispatch-ai-dataset`.
- Validate required columns exist.
- Display or log loaded row counts.

Acceptance criteria:

- AC-01.1: App starts locally from a documented command.
- AC-01.2: Dataset files load without private credentials.
- AC-01.3: The app or console shows row counts for jobs, vehicles, routes, and metrics.
- AC-01.4: README states that data is synthetic.

Tests:

- Verify each required dataset file exists.
- Verify required columns exist.
- Verify at least one baseline, optimized, and reoptimized route exists.

Traceability:

- FR-01, NFR-01, NFR-02, HN-01, HN-02.

### INC-02: Calculation Core

Goal: Implement deterministic metric and emissions calculations.

Scope:

- Fuel calculation.
- EV energy calculation.
- CO2e calculation.
- Idle calculation.
- Utilization calculation.
- Baseline vs optimized reduction calculation.

Acceptance criteria:

- AC-02.1: Calculated scenario totals match `metrics_by_scenario.csv` within rounding tolerance.
- AC-02.2: Calculated comparison values match `metrics_comparison.csv` within rounding tolerance.
- AC-02.3: Unit tests cover fuel, energy, CO2e, utilization, and reduction percentages.

Tests:

- `test_emissions.py`
- `test_metrics.py`

Traceability:

- FR-03, FR-05, FR-06, FR-07, NFR-03, HN-03.

### INC-03: Baseline Dispatch View

Goal: Show the current/manual baseline plan and assumptions.

Scope:

- Baseline route table.
- Baseline job assignments.
- Baseline KPI cards.
- Baseline assumptions panel.

Acceptance criteria:

- AC-03.1: User can view all baseline routes.
- AC-03.2: User can see jobs assigned to each baseline route.
- AC-03.3: Baseline KPIs include trips, distance, fuel, CO2e, idle time, SLA adherence, utilization, and operating cost index.
- AC-03.4: Baseline assumptions are visible.

Tests:

- Verify baseline route count is 6 for the supplied dataset.
- Verify baseline headline metrics match dataset.

Traceability:

- FR-02, FR-03, FR-07, HN-03.

### INC-04: Optimized Dispatch View

Goal: Show the optimized plan and before/after improvement.

Scope:

- Optimized route table.
- Optimized job assignments.
- Baseline vs optimized comparison.
- KPI deltas and reduction percentages.

Acceptance criteria:

- AC-04.1: User can view all optimized routes.
- AC-04.2: Dashboard shows baseline vs optimized side by side.
- AC-04.3: Dashboard highlights trips, distance, fuel, CO2e, idle time, planning time, and operating cost index reductions.
- AC-04.4: Each sustainability metric shows baseline and assumptions.

Tests:

- Verify optimized route count is 4 for the supplied dataset.
- Verify CO2e reduction is 18.5 kg / 29.8% for the supplied dataset.

Traceability:

- FR-04, FR-05, FR-06, FR-07, HN-03.

### INC-05: Constraint Validation

Goal: Validate route feasibility and make constraint checks visible.

Scope:

- Capacity validation.
- Time/SLA validation.
- Vehicle availability validation.
- Priority handling.
- Constraint result table.

Acceptance criteria:

- AC-05.1: Each route receives a constraint status.
- AC-05.2: Invalid routes show explicit failure reasons.
- AC-05.3: Constraint Agent trace references validation outputs.

Tests:

- `test_constraints.py`
- Test valid supplied routes.
- Test one intentionally invalid capacity case.
- Test one intentionally invalid SLA case.

Traceability:

- FR-09, NFR-03, HN-05.

### INC-06: Agent Workflow Trace

Goal: Demonstrate agentic orchestration rather than a single calculation screen.

Scope:

- Orchestrator step trace.
- Forecasting Agent trace.
- Carbon Intelligence Agent trace.
- Optimization Agent trace.
- Constraint Agent trace.
- Monitoring Agent trace placeholder until disruption increment.

Acceptance criteria:

- AC-06.1: User can inspect agent steps in order.
- AC-06.2: Each trace entry includes input summary, tool/function used, output summary, rationale, and status.
- AC-06.3: Trace shows deterministic calculators used for calculations.
- AC-06.4: Trace includes at least one feedback or validation handoff.

Tests:

- Verify all required agent names appear in trace.
- Verify each trace row has required fields.

Traceability:

- FR-08, HN-05, judging criterion "Agentic Depth & Technical Implementation".

### INC-07: Human Approval Workflow

Goal: Ensure humans approve high-impact recommendations.

Scope:

- Approval panel.
- Approve, reject, request revision controls.
- Decision audit log.
- Recommendation status.

Acceptance criteria:

- AC-07.1: Optimized plan starts in `needs_human_review` status.
- AC-07.2: User can approve, reject, or request revision.
- AC-07.3: Decision is recorded with timestamp/status.
- AC-07.4: UI states that agents recommend and humans approve.

Tests:

- Verify approval changes status.
- Verify rejection changes status.
- Verify request revision creates audit entry.

Traceability:

- FR-10, HN-04.

### INC-08: Disruption And Re-Optimization

Goal: Demonstrate dynamic re-planning.

Scope:

- Trigger disruption from `disruption_events.csv`.
- Show event details.
- Show reoptimized plan.
- Compare optimized vs reoptimized metrics.
- Update agent trace with Monitoring Agent action.

Acceptance criteria:

- AC-08.1: User can trigger the supplied disruption.
- AC-08.2: App displays the reoptimized route plan.
- AC-08.3: Monitoring Agent trace explains why reoptimization occurred.
- AC-08.4: Constraint Agent validates reoptimized plan.
- AC-08.5: Dashboard shows how disruption changes distance, fuel, CO2e, and route assignments.

Tests:

- Verify reoptimized scenario loads.
- Verify disruption event references affected vehicle.
- Verify reoptimized route count is 4 for supplied dataset.

Traceability:

- FR-11, FR-12, HN-05.

### INC-09: Agent Sustainability Panel

Goal: Prove the agent earns its keep.

Scope:

- Model-call count.
- Token estimate.
- Tool-call count.
- Retry count.
- Cache/reused calculation count.
- Deterministic calculator count.
- Optimization gain per model call.

Acceptance criteria:

- AC-09.1: Dashboard shows agent sustainability metrics.
- AC-09.2: Dashboard explains deterministic calculators reduce unnecessary model work.
- AC-09.3: App shows model/tool use alongside sustainability outcome.
- AC-09.4: Metrics are included in final demo summary.

Tests:

- Verify metric panel renders all required fields.
- Verify missing metric data produces a clear placeholder, not an error.

Traceability:

- FR-13, HN-06, judging criterion "Sustainability of the Agent Itself".

### INC-10: Decision Summary Export Or Display

Goal: Deliver results where the decision is made.

Scope:

- Concise summary panel.
- Baseline vs optimized headline metrics.
- Assumptions summary.
- Agent recommendation.
- Human approval status.

Acceptance criteria:

- AC-10.1: User can view a concise decision summary.
- AC-10.2: Summary includes baseline, optimized, reductions, assumptions, and approval status.
- AC-10.3: Summary is suitable for screenshot or demo close.

Tests:

- Verify summary includes CO2e avoided, distance avoided, fuel saved, and approval status.

Traceability:

- FR-14, HN-03.

### INC-11: Documentation And Submission Artifacts

Goal: Prepare the project for hackathon submission.

Scope:

- README.
- Agent design document.
- Assumptions document.
- Architecture diagram.
- Pitch deck outline under `submission/`.
- Demo script/storyboard under `submission/`.
- Open-source declaration.
- Known limitations.

Acceptance criteria:

- AC-11.1: README includes setup, run instructions, sample data, known limitations, data-safety statement, and open-source components.
- AC-11.2: Agent design document includes goal, users, data sources, tools, orchestration, decision points, human oversight, failure handling, privacy, auditability, and agent sustainability controls.
- AC-11.3: Architecture diagram includes user, scenario input, orchestrator, specialized agents, deterministic tools, synthetic data store, human approval gate, dashboard, and audit trail, with Mermaid source in `docs/architecture-diagram.mmd` and PNG rendering in `docs/architecture-diagram.png`.
- AC-11.4: Pitch deck outline has 8 to 10 slides.
- AC-11.5: Demo video storyboard is 3 to 5 minutes and shows the agent running.

Tests:

- Manual documentation checklist review.

Traceability:

- FR-15, FR-16, HN-07, HN-08, HN-09.

## 15. UI Specification

Recommended layout:

1. Scenario selector.
2. Baseline vs optimized KPI cards.
3. Route plan table.
4. Job assignment table.
5. Emissions and assumptions panel.
6. Agent trace panel.
7. Human approval panel.
8. Disruption and re-optimization panel.
9. Agent sustainability panel.
10. Decision summary panel.

UI requirements:

- The first screen must show the working dispatch dashboard, not a marketing page.
- Lead with operational KPIs and CO2e impact.
- Keep text compact and judge-friendly.
- Show assumptions where metrics are shown.
- Make route IDs, job IDs, vehicle IDs, and scenario IDs visible.

## 16. Testing Specification

Minimum test files:

| Test file | Coverage |
| --- | --- |
| `tests/test_emissions.py` | Fuel, energy, idle, CO2e formulas. |
| `tests/test_metrics.py` | Scenario totals, reductions, percentages. |
| `tests/test_constraints.py` | Capacity, SLA, availability, and invalid cases. |
| `tests/test_data_loading.py` | Dataset file and required-column checks. |
| `tests/test_agent_trace.py` | Agent trace fields and required agent roles. |

Manual demo checks:

- App starts from README command.
- Baseline metrics are visible.
- Optimized metrics are visible.
- Agent trace is visible.
- Human approval works.
- Disruption reoptimization works.
- Agent sustainability metrics are visible.

## 17. Traceability To Judging Criteria

| Judging criterion | Spec coverage |
| --- | --- |
| Sustainability Impact & Measurability | INC-02, INC-03, INC-04, INC-10 |
| Agentic Depth & Technical Implementation | INC-05, INC-06, INC-08 |
| Sustainability of the Agent Itself | INC-09 |
| Demo & Communication | INC-03, INC-04, INC-10, INC-11 |
| Innovation & Creativity | Full workflow: carbon-aware dispatch, human approval, disruption reoptimization, audit trail |

## 18. Definition Of Done

The project is done for hackathon submission when:

- The app runs locally from documented instructions.
- Synthetic data loads successfully.
- Baseline and optimized plans are visible.
- Before/after metrics are calculated and explained.
- CO2e methodology and assumptions are visible.
- Agent workflow trace is visible.
- Human approval step is visible.
- Disruption and reoptimization are visible.
- Agent sustainability metrics are visible.
- Tests cover data loading, emissions, metrics, constraints, and trace shape.
- README, agent design document, assumptions document, `submission/pitch-deck-outline.md`, and `submission/demo-storyboard.md` are complete.
- No customer, confidential, personal, or client-branded data is included.
- Open-source components and pre-existing components are declared.

## 19. Implementation Notes

- Prefer Streamlit and Python for fastest delivery unless the team chooses another stack.
- Keep the optimization initially heuristic and explainable.
- Google OR-Tools is optional and should be considered only after the heuristic optimizer is demo-ready and time remains.
- Keep calculations deterministic and separated from agent narration.
- Use agent trace as the main evidence of agentic depth.
- Use dataset replay if live optimization is not complete, but clearly label replayed/generated data.
- Keep every increment demoable.
