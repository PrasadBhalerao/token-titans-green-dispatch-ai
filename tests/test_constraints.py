import unittest

from src.core.constraints import validate_routes
from src.core.data_loader import load_dataset


class ConstraintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()
        cls.vehicles = cls.dataset.table("vehicles")
        cls.jobs = cls.dataset.table("jobs")

    def test_supplied_optimized_routes_pass(self):
        routes = self.dataset.scenario_rows("plan_routes", "optimized")
        results = validate_routes(routes, self.vehicles, self.jobs)
        self.assertTrue((results["status"] == "pass").all())

    def test_invalid_capacity_case_fails(self):
        routes = self.dataset.scenario_rows("plan_routes", "optimized")
        invalid = routes.head(1).copy()
        invalid.loc[invalid.index[0], "total_demand_kg"] = 9999
        results = validate_routes(invalid, self.vehicles, self.jobs)
        self.assertEqual(results.iloc[0]["status"], "fail")
        self.assertIn("weight capacity", results.iloc[0]["reasons"])

    def test_invalid_sla_case_fails(self):
        routes = self.dataset.scenario_rows("plan_routes", "optimized")
        invalid = routes.head(1).copy()
        invalid.loc[invalid.index[0], "total_route_minutes"] = 999
        results = validate_routes(invalid, self.vehicles, self.jobs)
        self.assertEqual(results.iloc[0]["status"], "fail")
        self.assertIn("due time", results.iloc[0]["reasons"])


if __name__ == "__main__":
    unittest.main()
