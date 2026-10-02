# GreenDispatch AI Dataset Pack

This folder contains a hackathon-ready synthetic dataset for the GreenDispatch AI proof of concept.

The data is intentionally synthetic: no customer, personal, confidential, or client-branded data is included. The fuel and energy assumptions are realistic demo assumptions derived from public transport-emissions methodology and real-world telemetry patterns, not from any private fleet.

## Files

- locations.csv - synthetic depot and customer/service locations.
- jobs.csv - synthetic dispatch and field-service jobs with time windows.
- vehicles.csv - vehicle capacity, fuel/energy rates, idle rates, emission factors, and cost index.
- distance_matrix.csv - complete synthetic distance/time matrix generated from stop coordinates.
- emission_factors.csv - CO2e factors used in the demo.
- fuel_usage_profiles.csv - realistic fuel/energy usage profiles used for synthesis.
- plan_routes.csv - route-level baseline, optimized, and reoptimized plans.
- plan_legs.csv - leg-level distances and travel times.
- plan_assignments.csv - job-to-route mapping.
- metrics_by_scenario.csv - scenario totals.
- metrics_comparison.csv - baseline vs optimized improvements.
- disruption_events.csv - disruption scenario for dynamic replanning demo.
- standard_dataset_sources.csv - public benchmark datasets considered for later extension.
- scenarios.json - app-friendly scenario metadata and formulas.

## Measurement Formulas

Fuel vehicle:

```text
fuel_liters = distance_km * fuel_rate_l_per_100km / 100
idle_fuel_liters = idle_minutes * idle_fuel_l_per_hour / 60
co2e_kg = (fuel_liters + idle_fuel_liters) * kgCO2e_per_liter
```

Electric vehicle:

```text
energy_kwh = distance_km * energy_rate_kwh_per_100km / 100
idle_energy_kwh = idle_minutes * idle_energy_kwh_per_hour / 60
co2e_kg = (energy_kwh + idle_energy_kwh) * kgCO2e_per_kwh
```

Optimization delta:

```text
reduction = baseline_value - optimized_value
reduction_pct = reduction / baseline_value * 100
```

## Source Notes

- GHG Protocol guidance says actual fuel-use data is the preferred basis for transport emissions, while distance- or spend-based estimates can be used when fuel data is unavailable.
- Geotab and Samsara both expose fuel/energy usage through fleet telematics APIs, which is how a production version would obtain measured fuel-use data.
- The Vehicle Energy Dataset (VED) includes real OBD-II fuel-rate and energy telemetry and can be used later to calibrate more advanced fuel models.
- Central Electricity Authority publishes India's CO2 Baseline Database; this demo uses an India-grid-style factor of 0.71 kgCO2e/kWh for EV charging calculations.
- DCCEEW National Greenhouse Accounts Factors are used as a transparent public source for demo fuel emission factors.

## Public References

- GHG Protocol transport calculation guidance: https://ghgptechassistance.zendesk.com/hc/en-us/articles/37791078550420-How-do-I-calculate-emissions-from-transportation
- Geotab FuelUsed API object: https://developers.geotab.com/myGeotab/apiReference/objects/FuelUsed/
- Samsara Fuel and Energy vehicle reports: https://developers.samsara.com/reference/getfuelenergyvehiclereports
- Vehicle Energy Dataset: https://github.com/gsoh/VED
- CEA CO2 Baseline Database: https://cea.nic.in/cdm-co2-baseline-database/?lang=en
- DCCEEW NGA Factors 2026: https://www.dcceew.gov.au/climate-change/publications/national-greenhouse-accounts-factors-2026

## Recommended Hackathon Use

1. Load jobs.csv, vehicles.csv, locations.csv, and distance_matrix.csv into the prototype.
2. Display the baseline scenario from plan_routes.csv and metrics_by_scenario.csv.
3. Run the agentic optimizer or replay the optimized scenario.
4. Show metrics_comparison.csv as the headline impact.
5. Trigger disruption_events.csv and show the reoptimized scenario.

## Caveats

- Distances are synthetic road-like distances, not map-provider distances.
- Fuel rates are realistic planning estimates, not measured from a specific vehicle.
- Emission factors are included for hackathon traceability and should be replaced with customer-region factors in a production deployment.
