# GreenDispatch AI Project Instructions

These instructions guide all implementation, documentation, demo, and artifact work for the Sustainability Hackathon Team Token Titans project.

## Source Of Truth

Use these documents as the primary project references:

- `docs/hackathon-details.md` - official hackathon requirements, rules, judging criteria, and required artifacts.
- `docs/greendispatch-ai-implementation-plan.md` - GreenDispatch AI solution plan, architecture, implementation phases, metrics, and artifact plan.
- `data/greendispatch-ai-dataset/README.md` - dataset assumptions, formulas, synthetic data notes, and measurement methodology.

If the project plan conflicts with the hackathon brief, the hackathon brief wins.

## Product Goal

Build GreenDispatch AI, an agentic carbon-aware scheduling and dispatch optimizer.

The prototype must help a planner compare:

```text
Baseline dispatch plan -> Agentic optimized dispatch plan
```

The app must quantify operational and sustainability impact using before/after metrics such as trips, distance, fuel or energy use, CO2e emissions, idle time, utilization, SLA adherence, and planning time.

## Hackathon Non-Negotiables

- Use only public, open, or synthetic data.
- Do not use customer code, customer data, confidential data, personal data, or client branding.
- Clearly state all assumptions for emissions, fuel, energy, routing, and planning time.
- State the baseline and assumptions beside every claimed sustainability impact metric.
- Include human approval before any high-impact dispatch decision is considered final.
- Show that the solution is genuinely agentic: planning, tool use, orchestration, traceability, error handling, feedback, and re-planning.
- Include agent sustainability metrics such as model calls, token usage, tool calls, retries, cache usage, and deterministic calculator usage.
- Declare all open-source components in the README.
- Ensure all submitted work is original. Pre-existing or open-source components must be declared, and plagiarism is disqualifying.
- Reference recognized sustainability standards where useful, such as SCI / ISO/IEC 21031:2024, GHG Protocol, ESRS, or ISSB.
- Keep the demo runnable without external private systems.

## Solution Scope

The hackathon proof of concept should focus on a controlled synthetic dispatch scenario:

- 8 to 20 jobs.
- 3 to 6 vehicles or mobile assets.
- Vehicle capacity, fuel or energy rates, emission factors, and cost index.
- Distance and travel-time matrix.
- SLA windows, priority, service time, and disruption event.
- Baseline route plan.
- Optimized agentic route plan.
- Re-optimized plan after a disruption.

Out of scope for the hackathon build:

- Live customer integrations.
- Real customer data.
- Autonomous dispatch execution.
- Financially, legally, contractually, or reputationally binding actions.
- Production-grade routing engine dependency unless time allows.

## Required User Experience

The first usable screen should be the working dispatch optimizer or dashboard, not a marketing page.

The app should let the user:

- Load or select the synthetic scenario.
- View the baseline dispatch plan.
- Run or replay the agentic optimization.
- Compare baseline vs optimized KPIs.
- Inspect route/job assignments.
- Inspect emissions and fuel/energy assumptions.
- Inspect agent trace and rationale.
- Trigger a disruption scenario.
- View the re-optimized plan.
- Approve, reject, or request revision of the recommended plan.
- Export or display a concise result summary where the dispatch decision is made, not only as a retrospective report.

## Agent Architecture

Implement or simulate the following agent roles:

| Agent | Responsibility |
| --- | --- |
| Orchestrator Agent | Coordinates the workflow, calls specialized agents/tools, manages retries, and produces final recommendation. |
| Forecasting Agent | Estimates load, priority pressure, and SLA-sensitive work from job data. |
| Carbon Intelligence Agent | Calculates fuel/energy use and CO2e emissions using documented factors. |
| Optimization Agent | Generates candidate dispatch plans and improves distance, trips, utilization, fuel, and emissions. |
| Constraint Agent | Validates capacity, SLA, availability, priority, and operational constraints. |
| Monitoring Agent | Detects disruption and triggers re-optimization. |

Use deterministic functions for calculations and validation. Use agent reasoning for orchestration, trade-off explanation, exception handling, and recommendation narrative.

## Measurement Requirements

Always compare baseline vs optimized plan.

Minimum operational metrics:

- Trips.
- Vehicles used.
- Total distance.
- Total travel time.
- Total idle time.
- SLA adherence.
- Capacity utilization.
- Operating cost index.

Minimum sustainability metrics:

- Fuel saved.
- Energy saved, if EV is used.
- CO2e avoided.
- CO2e reduction percentage.
- Baseline and assumptions for every sustainability calculation.

Minimum agent sustainability metrics:

- Agent steps.
- Model calls.
- Actual OpenAI input/output/total token usage when live LLM mode runs; zero actual LLM tokens when deterministic fallback is used.
- Tool calls.
- Retry count.
- Cache hits or reused calculations.
- Deterministic calculator calls.
- Optimization gain per model call.

Use these formulas unless replaced by better documented formulas:

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

## Incremental Build Order

Build in small, demonstrable increments. Each increment should leave the project runnable or verifiable.

### Increment 1: Data Loading

Acceptance criteria:

- Load jobs, vehicles, locations, distance matrix, plans, and metrics from `data/greendispatch-ai-dataset`.
- Show raw scenario data in a simple table or console output.
- Confirm data is synthetic in the UI or README.

### Increment 2: Calculation Core

Acceptance criteria:

- Implement emissions calculation.
- Implement distance, fuel, energy, idle, CO2e, utilization, and reduction metrics.
- Add tests for emissions and metric formulas.
- Match generated dataset totals within rounding tolerance.

### Increment 3: Baseline Plan View

Acceptance criteria:

- Display baseline routes, jobs, vehicles, distance, fuel, CO2e, idle time, and SLA status.
- Explain baseline assumptions.

### Increment 4: Optimized Plan View

Acceptance criteria:

- Display optimized routes and KPIs.
- Display baseline vs optimized comparison.
- Highlight reductions in trips, distance, fuel, CO2e, idle time, and planning time.

### Increment 5: Agent Workflow Trace

Acceptance criteria:

- Show Orchestrator, Forecasting, Carbon, Optimization, Constraint, and Monitoring agent steps.
- Show inputs, outputs, and reasoning summary for each agent.
- Show failed candidate or constraint rejection examples if available.

### Increment 6: Human Approval

Acceptance criteria:

- User can approve, reject, or request revision.
- Approval decision is recorded in the audit trail.
- The UI clearly states that agents recommend but humans approve.

### Increment 7: Disruption And Re-Optimization

Acceptance criteria:

- Trigger the provided disruption event.
- Display the re-optimized plan.
- Compare optimized vs re-optimized deltas.
- Show Monitoring Agent action and Constraint Agent validation.

### Increment 8: Agent Sustainability Panel

Acceptance criteria:

- Display model calls, token usage, tool calls, retries, deterministic calculator usage, and cache reuse.
- Explain how deterministic calculators reduce unnecessary model work.

### Increment 9: Final Demo Polish

Acceptance criteria:

- App runs from documented setup command.
- README contains setup, run instructions, sample data description, known limitations, open-source components, and data-safety statement.
- Agent design document is complete.
- Demo script and pitch deck outline are ready under `submission/`.

## Repository Structure

Target structure:

```text
Sustainability Hackathon - Team Token Titans/
  README.md
  INSTRUCTIONS.md
  app.py
  requirements.txt
  data/
    greendispatch-ai-dataset/
    user-edited-scenarios/
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

The project may start smaller, but new code should move toward this structure.

## Implementation Guidance

- Prefer a simple runnable prototype over a complex unfinished system.
- Use deterministic Python functions for math, validation, scoring, and metrics.
- Keep agent inputs and outputs structured as dictionaries or JSON-like objects.
- Keep prompts short, role-specific, and traceable.
- Cache repeated distance, emissions, and metric calculations.
- Make assumptions visible to judges.
- Use clear route IDs, vehicle IDs, job IDs, and scenario IDs.
- Keep errors understandable in the UI.
- Add tests for calculation-heavy code before polishing visuals.

## Dashboard Guidance

The dashboard should be operational and compact.

Recommended sections:

- Scenario selector.
- Baseline vs optimized KPI cards.
- Route plan table.
- Job assignment table.
- Emissions and assumptions panel.
- Agent trace panel.
- Human approval panel.
- Disruption and re-optimization panel.
- Agent sustainability panel.

Lead with the five strongest KPIs:

- Trips reduced.
- Distance avoided.
- Fuel or energy saved.
- CO2e avoided.
- Idle or planning time reduced.

## Documentation Requirements

Final submission documentation must include:

- Proof of concept README.
- Agent design document.
- Architecture diagram.
- Assumptions and emissions methodology.
- Known limitations.
- Open-source component declaration.
- Data safety statement.
- Agent sustainability explanation.
- Pitch deck with 8 to 10 slides under `submission/`.
- Demo video script or storyboard under `submission/`.
- Demo video, 3 to 5 minutes, showing the agent running rather than only a slide walkthrough.

## Final Submission Checklist

- [ ] Working proof of concept runs locally.
- [ ] Synthetic data included.
- [ ] Setup and run instructions are complete.
- [ ] Baseline vs optimized dispatch comparison is visible.
- [ ] CO2e methodology and assumptions are documented.
- [ ] Agent workflow trace is visible.
- [ ] Human approval step is visible.
- [ ] Disruption and re-optimization scenario is visible.
- [ ] Agent sustainability metrics are visible.
- [ ] Tests cover emissions, constraints, and metrics.
- [ ] Agent design document includes architecture, data sources, tools, orchestration, decision points, human oversight, and failure handling.
- [ ] Pitch deck has 8 to 10 slides.
- [ ] Demo video is 3 to 5 minutes.
- [ ] No customer, confidential, personal, or client-branded data is included.
- [ ] Open-source components are declared.

## Review Standard

Before marking work complete, verify it helps the judges see:

- What sustainability problem is being solved.
- Why agentic AI is needed.
- How the agents work together.
- What changed between baseline and optimized dispatch.
- How the impact was measured.
- Why the agent's own compute footprint is justified.
- Where human approval and auditability fit.
