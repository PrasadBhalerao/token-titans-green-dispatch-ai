# Sustainability Hackathon - Team Token Titans

Project workspace for the GreenDispatch AI hackathon submission.

## Solution

GreenDispatch AI - Agentic Carbon-Aware Scheduling & Dispatch Optimizer

Tagline: Optimize every dispatch for operations, cost, and carbon.

## What It Does

GreenDispatch AI compares a manual baseline dispatch plan against an agentic optimized plan, quantifies distance, fuel, CO2e, idle-time, planning-time, and cost-index reductions, validates operational constraints, and keeps a human approval gate before the recommendation is finalized.

The prototype uses a local synthetic dataset and stores generated run artifacts under `outputs/runs/<run_id>/`.

## How To Run

From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

Open the Streamlit URL shown in the terminal. The dashboard is the first screen.

Windows shortcut:

```powershell
.\run_app.ps1
```

## Live OpenAI Mode

The dashboard uses deterministic local agent logic by default. To enable live LLM-assisted optimization when clicking **Run optimization**, set an OpenAI API key before starting Streamlit:

```powershell
$env:OPENAI_API_KEY="your-api-key"
```

Optional model override:

```powershell
$env:GREEN_DISPATCH_OPENAI_MODEL="gpt-4o-mini"
```

If no API key is present, the app falls back to the current deterministic agent workflow and reports zero actual LLM tokens. The reusable LLM optimizer prompt is stored at `prompts/dispatch_optimizer_prompt.md`.

## How To Test

```powershell
pytest
```

If pytest is not installed yet, the tests can also run with the standard library test runner:

```powershell
python -m unittest discover -s tests -v
```

## Current Structure

```text
Sustainability Hackathon - Team Token Titans/
  app.py
  requirements.txt
  README.md
  INSTRUCTIONS.md
  TASK.md
  data/
    greendispatch-ai-dataset/
    greendispatch-ai-dataset.zip
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
  outputs/
    runs/
  prompts/
    dispatch_optimizer_prompt.md
  src/
    agents/
    core/
    ui/
  submission/
    README.md
    pitch-deck-outline.md
    demo-storyboard.md
  tests/
```

## Key Documents

- `docs/hackathon-details.md` - hackathon brief extracted from the SharePoint page.
- `docs/greendispatch-ai-implementation-plan.md` - implementation plan, architecture, artifacts, demo plan, and judging alignment.
- `docs/greendispatch-ai-spec.md` - incremental spec-driven development requirements.
- `docs/python-streamlit-code-guidelines.md` - Python and Streamlit coding and review standards.
- `docs/agent-design.md` - project design, agent responsibilities, data flow, and storage model.
- `docs/architecture-diagram.mmd` - canonical Mermaid architecture diagram.
- `docs/architecture-diagram.png` - rendered architecture diagram for docs, deck, and demo walkthrough.
- `docs/assumptions.md` - emissions, data, optimization, and demo assumptions.
- `submission/pitch-deck-outline.md` - pitch deck outline.
- `submission/demo-storyboard.md` - 3 to 5 minute demo storyboard.

## Dataset

The dataset is synthetic and hackathon-safe. It includes jobs, vehicles, locations, distance matrix, emissions factors, fuel/energy profiles, route plans, scenario metrics, and a disruption scenario.

Headline optimized-plan impact:

| Metric | Baseline | Optimized | Reduction |
| --- | ---: | ---: | ---: |
| Trips | 6 | 4 | 33.3% |
| Distance | 190.82 km | 137.22 km | 28.1% |
| Fuel | 23.31 L | 15.13 L | 35.1% |
| CO2e | 62.14 kg | 43.64 kg | 29.8% |
| Idle time | 113 min | 39 min | 65.5% |

## Demo Flow

1. Load the synthetic dispatch dataset.
2. Review the baseline route plan and assumptions.
3. Run the agentic workflow.
4. Compare baseline and optimized metrics.
5. Inspect agent trace and constraint validation.
6. Approve, reject, or request revision as the human planner.
7. Trigger the supplied vehicle-unavailable disruption.
8. Review the reoptimized plan and agent sustainability metrics.
9. Close with the decision summary.

## Data Safety

- No customer, confidential, personal, or client-branded data is included.
- All source data is synthetic and stored locally under `data/greendispatch-ai-dataset/`.
- User-edited scenarios are stored separately under `data/user-edited-scenarios/`.
- Generated run artifacts are stored under `outputs/runs/<run_id>/`.

## Open-Source Components

- Python - application language.
- Streamlit - dashboard UI.
- pandas - data loading and calculation tables.
- Plotly - comparison charts.
- OpenAI Python SDK - optional live LLM-assisted optimizer.
- pytest - test runner.

Google OR-Tools is not required for the current demo. It may be considered after the heuristic/demo optimizer is stable.

## Known Limitations

- Routes are replayed from the synthetic optimized and reoptimized dataset rather than solved by a production-grade route solver.
- Distances are synthetic road-like distances, not live map-provider distances.
- Fuel and energy rates are realistic planning assumptions, not measured telematics for a real fleet.
- Human approval is local demo state and JSON output, not an enterprise workflow integration.
- Streamlit local file storage is sufficient for the hackathon demo, not production multi-user storage.
