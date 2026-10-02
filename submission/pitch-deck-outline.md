# GreenDispatch AI Pitch Deck Outline

## Slide 1: Title

GreenDispatch AI - Agentic Carbon-Aware Scheduling & Dispatch Optimizer  
Optimize every dispatch for operations, cost, and carbon.

## Slide 2: Problem

Dispatch plans often optimize for availability, cost, and timing while carbon impact is measured later. This creates avoidable trips, distance, idle time, fuel use, and CO2e emissions.

## Slide 3: Users And Pain

Dispatch planners need feasible plans fast. Fleet managers need utilization and cost control. Sustainability teams need measurable CO2e impact with assumptions. Operations leaders need approval-ready evidence.

## Slide 4: Solution

GreenDispatch AI uses an orchestrator plus specialized agents to compare baseline and optimized plans, validate constraints, quantify impact, and keep human approval in the workflow.

## Slide 5: How It Works

Show the architecture: Streamlit dashboard, local synthetic data, orchestrator, forecasting agent, carbon intelligence agent, optimization agent, constraint agent, monitoring agent, deterministic calculators, and run artifacts.

## Slide 6: Demo Scenario

Baseline: 6 trips, 190.82 km, 23.31 L fuel, 62.14 kgCO2e.  
Optimized: 4 trips, 137.22 km, 15.13 L fuel, 43.64 kgCO2e.

## Slide 7: Measured Impact

CO2e avoided: 18.5 kg.  
Distance avoided: 53.6 km.  
Fuel saved: 8.18 L.  
Trips consolidated: 2.  
Idle time reduced: 74 minutes.

## Slide 8: Agentic Depth

Show the structured agent trace, deterministic tool usage, constraint validation, disruption monitoring, and reoptimization path.

## Slide 9: Agent Sustainability

Show model calls, token estimates, tool calls, retries, deterministic calculator usage, cache reuse, and impact per model call.

## Slide 10: Roadmap And Close

Next steps: integrate real telematics fuel data, route APIs, ERP/TMS/FSM systems, OR-Tools solver, and live monitoring.  
Close: sustainability becomes an operational decision, not an after-the-fact report.
