import unittest

from src.core.data_loader import load_dataset
from src.core.metrics import calculate_scenario_metrics, compare_scenarios


class MetricsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.metrics = calculate_scenario_metrics(
            cls.dataset.table("plan_routes"),
            cls.dataset.table("metrics_by_scenario"),
        )
        cls.comparison = compare_scenarios(cls.metrics)

    def test_scenario_totals_match_reference(self):
        reference = self.dataset.table("metrics_by_scenario").set_index("scenario")
        calculated = self.metrics.set_index("scenario")
        for scenario in ["baseline", "optimized", "fuel_optimized", "distance_optimized", "reoptimized"]:
            with self.subTest(scenario=scenario):
                self.assertAlmostEqual(calculated.loc[scenario, "total_distance_km"], reference.loc[scenario, "total_distance_km"], places=2)
                self.assertAlmostEqual(calculated.loc[scenario, "total_fuel_liters"], reference.loc[scenario, "total_fuel_liters"], places=2)
                self.assertAlmostEqual(calculated.loc[scenario, "total_co2e_kg"], reference.loc[scenario, "total_co2e_kg"], places=2)
                self.assertAlmostEqual(calculated.loc[scenario, "operating_cost_index"], reference.loc[scenario, "operating_cost_index"], places=2)

    def test_headline_comparison_values(self):
        comparison = self.comparison.set_index("metric")
        self.assertEqual(comparison.loc["trips", "baseline"], 6)
        self.assertEqual(comparison.loc["trips", "optimized"], 4)
        self.assertAlmostEqual(comparison.loc["distance", "absolute_reduction"], 53.6, places=2)
        self.assertAlmostEqual(comparison.loc["distance", "reduction_pct"], 28.1, places=1)
        self.assertAlmostEqual(comparison.loc["fuel", "absolute_reduction"], 8.18, places=2)
        self.assertAlmostEqual(comparison.loc["co2e", "absolute_reduction"], 18.5, places=2)
        self.assertAlmostEqual(comparison.loc["idle_time", "absolute_reduction"], 74, places=2)

    def test_fuel_and_distance_scenarios_optimize_different_objectives(self):
        calculated = self.metrics.set_index("scenario")
        self.assertLess(
            calculated.loc["fuel_optimized", "total_fuel_liters"],
            calculated.loc["optimized", "total_fuel_liters"],
        )
        self.assertLess(
            calculated.loc["distance_optimized", "total_distance_km"],
            calculated.loc["optimized", "total_distance_km"],
        )
        self.assertLess(
            calculated.loc["optimized", "total_co2e_kg"],
            calculated.loc["fuel_optimized", "total_co2e_kg"],
        )
        self.assertLess(
            calculated.loc["optimized", "total_co2e_kg"],
            calculated.loc["distance_optimized", "total_co2e_kg"],
        )


if __name__ == "__main__":
    unittest.main()
