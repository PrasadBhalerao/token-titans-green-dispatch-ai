import unittest

from src.core.data_loader import load_dataset
from src.core.emissions import (
    calculate_co2e,
    calculate_energy_kwh,
    calculate_fuel_liters,
    calculate_route_energy_and_emissions,
)


class EmissionsTests(unittest.TestCase):
    def test_fuel_formula(self):
        liters = calculate_fuel_liters(
            distance_km=17.63,
            fuel_rate_l_per_100km=9.8,
            idle_minutes=16,
            idle_fuel_l_per_hour=0.8,
        )
        self.assertAlmostEqual(liters, 1.94, places=2)
        self.assertAlmostEqual(calculate_co2e(liters, 2.71), 5.26, places=2)

    def test_ev_energy_formula(self):
        energy = calculate_energy_kwh(
            distance_km=24.57,
            energy_rate_kwh_per_100km=22,
            idle_minutes=8,
            idle_energy_kwh_per_hour=0.8,
        )
        self.assertAlmostEqual(energy, 5.51, places=2)
        self.assertAlmostEqual(calculate_co2e(energy, 0.71), 3.91, places=2)

    def test_route_emissions_match_dataset_route(self):
        dataset = load_dataset()
        route = dataset.scenario_rows("plan_routes", "optimized").iloc[0].to_dict()
        vehicle = dataset.table("vehicles").set_index("vehicle_id").loc[route["vehicle_id"]].to_dict()
        result = calculate_route_energy_and_emissions(route, vehicle)
        self.assertAlmostEqual(result["energy_kwh"], route["energy_kwh"], places=2)
        self.assertAlmostEqual(result["co2e_kg"], route["co2e_kg"], places=2)


if __name__ == "__main__":
    unittest.main()
