# GreenDispatch AI Demo Storyboard

Target length: 3 to 5 minutes.

## 0:00-0:30 - Set The Context

Open the Streamlit dashboard. Explain that the data is synthetic and the goal is to compare manual dispatch against carbon-aware optimized dispatch.

## 0:30-1:00 - Show Baseline

Open the Baseline tab. Show the 6 baseline routes, job assignments, assumptions, and baseline KPIs.

Key line: "The current plan works operationally, but it creates extra distance, fuel use, idle time, and CO2e."

## 1:00-1:45 - Show Optimized Plan

Open the Optimized tab. Show the comparison chart, 4 optimized routes, and constraint validation.

Key line: "The optimized plan consolidates trips while preserving capacity and SLA constraints."

## 1:45-2:20 - Show Agent Trace

Open the Agents tab. Walk through Orchestrator, Forecasting, Carbon Intelligence, Optimization, Constraint, and Monitoring Agent rows.

Key line: "Agents do not perform hidden arithmetic; deterministic tools calculate emissions, metrics, and constraints."

## 2:20-2:50 - Human Approval

Return to Optimized. Show status `needs_human_review`, then approve or request revision.

Key line: "The system recommends. The human planner approves."

## 2:50-3:30 - Trigger Disruption

Open Disruption. Trigger the supplied vehicle-unavailable event and show the reoptimized plan.

Key line: "When conditions change, the Monitoring Agent triggers reoptimization and the Constraint Agent validates the revised plan."

## 3:30-4:15 - Show Sustainability Impact

Open Sustainability and Summary. Show CO2e avoided, distance avoided, fuel saved, trips consolidated, idle time reduced, and agent sustainability metrics.

Key line: "GreenDispatch AI makes sustainability measurable at the moment the dispatch decision is made."

## 4:15-5:00 - Close

Summarize the impact, limitations, and roadmap: real telematics fuel data, route APIs, enterprise dispatch integrations, and optional OR-Tools optimization after the demo-ready heuristic workflow.
