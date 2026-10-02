import unittest

from src.core.data_loader import REQUIRED_COLUMNS, REQUIRED_FILES, load_dataset


class DataLoadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset()

    def test_required_files_and_tables_load(self):
        for name in REQUIRED_FILES:
            with self.subTest(table=name):
                self.assertIn(name, self.dataset.tables)
                self.assertGreaterEqual(len(self.dataset.table(name)), 1)

    def test_required_columns_exist(self):
        for name, columns in REQUIRED_COLUMNS.items():
            with self.subTest(table=name):
                self.assertTrue(columns.issubset(set(self.dataset.table(name).columns)))

    def test_expected_scenarios_exist(self):
        routes = self.dataset.table("plan_routes")
        self.assertEqual(len(routes[routes["scenario"] == "baseline"]), 6)
        self.assertEqual(len(routes[routes["scenario"] == "optimized"]), 4)
        self.assertEqual(len(routes[routes["scenario"] == "fuel_optimized"]), 4)
        self.assertEqual(len(routes[routes["scenario"] == "distance_optimized"]), 4)
        self.assertEqual(len(routes[routes["scenario"] == "reoptimized"]), 4)


if __name__ == "__main__":
    unittest.main()
