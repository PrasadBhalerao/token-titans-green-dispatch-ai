# GreenDispatch AI Assumptions

## Data Assumptions

- All dispatch, vehicle, route, location, and disruption records are synthetic.
- The dataset contains no customer, confidential, personal, or client-branded data.
- `data/greendispatch-ai-dataset/` is treated as read-only source demo data.
- User-edited scenarios are saved as JSON under `data/user-edited-scenarios/`.
- Generated run outputs are saved under `outputs/runs/<run_id>/`.

## Fuel, Energy, And Emissions Assumptions

- Fuel vehicles use:

```text
fuel_liters = distance_km * fuel_rate_l_per_100km / 100
idle_fuel_liters = idle_minutes * idle_fuel_l_per_hour / 60
co2e_kg = (fuel_liters + idle_fuel_liters) * kgCO2e_per_liter
```

- Electric vehicles use:

```text
energy_kwh = distance_km * energy_rate_kwh_per_100km / 100
idle_energy_kwh = idle_minutes * idle_energy_kwh_per_hour / 60
co2e_kg = (energy_kwh + idle_energy_kwh) * kgCO2e_per_kwh
```

- Diesel and petrol factors are demo factors based on public greenhouse-accounting references.
- EV emissions use the included grid-emissions factor in `emission_factors.csv`.
- Production use should replace demo factors with region-specific and fleet-specific measured values.

## Optimization Assumptions

- The hackathon prototype replays the prepared `optimized` and `reoptimized` scenarios from `plan_routes.csv`.
- This keeps the demo deterministic, inspectable, and safe for a short judging window.
- The initial optimizer is heuristic/demo-oriented; Google OR-Tools is optional after the demo workflow is stable.
- Human approval remains mandatory before the optimized plan is considered final.

## Constraint Assumptions

- Route weight capacity must not exceed vehicle weight capacity.
- Route volume capacity allows a small 5% tolerance to account for synthetic-data rounding.
- SLA validation checks route completion against the earliest assigned due time using a 09:00 route start.
- Vehicle unavailability is applied during the disruption/reoptimization flow.

## Agent Sustainability Assumptions

- If `OPENAI_API_KEY` is configured and the user clicks **Run optimization**, the app calls the live OpenAI optimizer and records input, output, and total tokens from the API response usage metadata.
- If the API key is unavailable, the SDK is unavailable, or the live call fails, the app falls back to deterministic local agent logic and records zero actual LLM tokens for that run.
- Deterministic calculators are used for math, metrics, emissions, and constraints to avoid unnecessary model work.
- The agent trace is structured JSON so judges can inspect what each agent did.
