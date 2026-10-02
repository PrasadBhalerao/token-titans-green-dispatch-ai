import unittest

import pandas as pd

from src.agents.common import TRACE_FIELDS
from src.agents.orchestrator import run_dispatch_workflow
from src.core.data_loader import load_dataset


class AgentTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = run_dispatch_workflow(load_dataset(), persist=False, use_live_llm=False)

    def test_required_agent_roles_appear(self):
        agents = {row["agent_name"] for row in self.workflow["trace"]}
        self.assertIn("Orchestrator Agent", agents)
        self.assertIn("Forecasting Agent", agents)
        self.assertIn("Carbon Intelligence Agent", agents)
        self.assertIn("Optimization Agent", agents)
        self.assertIn("Constraint Agent", agents)
        self.assertIn("Monitoring Agent", agents)

    def test_trace_shape(self):
        for row in self.workflow["trace"]:
            with self.subTest(agent=row["agent_name"]):
                self.assertTrue(set(TRACE_FIELDS).issubset(row.keys()))
                self.assertTrue(row["step_id"])
                self.assertTrue(row["tool_or_function_used"])
                self.assertIn(row["status"], {"completed", "warning", "rejected", "needs_human_review"})

    def test_decision_summary_includes_required_headlines(self):
        headline = self.workflow["decision_summary"]["headline"]
        self.assertIn("co2e_avoided_kg", headline)
        self.assertIn("distance_avoided_km", headline)
        self.assertIn("fuel_saved_liters", headline)
        self.assertEqual(self.workflow["decision_summary"]["approval_status"], "needs_human_review")

    def test_deterministic_fallback_reports_zero_llm_tokens(self):
        sustainability = self.workflow["agent_sustainability"]
        self.assertEqual(sustainability["execution_mode"], "deterministic_fallback")
        self.assertEqual(sustainability["total_tokens"], 0)
        self.assertEqual(sustainability["input_tokens"], 0)
        self.assertEqual(sustainability["output_tokens"], 0)
        self.assertEqual(sustainability["model_calls"], 0)

    def test_new_workload_impacts_optimized_plan(self):
        dataset = load_dataset()
        edited_jobs = pd.concat(
            [
                dataset.table("jobs"),
                pd.DataFrame(
                    [
                        {
                            "job_id": "J_NEW",
                            "destination_id": "L01",
                            "job_type": "delivery",
                            "demand_kg": 100,
                            "volume_m3": 1.0,
                            "priority": "high",
                            "ready_time": "09:00",
                            "due_time": "17:00",
                            "service_minutes": 15,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

        workflow = run_dispatch_workflow(
            dataset,
            edited_jobs=edited_jobs,
            persist=False,
            use_live_llm=False,
        )
        optimized_routes = workflow["routes"][workflow["routes"]["scenario"] == "optimized"]
        optimized_assignments = workflow["assignments"][workflow["assignments"]["scenario"] == "optimized"]
        optimized_metrics = workflow["metrics"][workflow["metrics"]["scenario"] == "optimized"].iloc[0]
        fuel_routes = workflow["routes"][workflow["routes"]["scenario"] == "fuel_optimized"]
        distance_routes = workflow["routes"][workflow["routes"]["scenario"] == "distance_optimized"]

        self.assertIn("J_NEW", set(workflow["jobs"]["job_id"]))
        self.assertIn("O_NEW_01", set(optimized_routes["route_id"]))
        self.assertIn("F_NEW_01", set(fuel_routes["route_id"]))
        self.assertIn("D_NEW_01", set(distance_routes["route_id"]))
        self.assertIn("J_NEW", set(optimized_assignments["job_id"]))
        self.assertEqual(int(optimized_metrics["trips"]), 5)
        self.assertGreater(float(optimized_metrics["total_distance_km"]), 137.22)
        self.assertTrue((workflow["optimized_constraints"]["status"] == "pass").all())


if __name__ == "__main__":
    unittest.main()
