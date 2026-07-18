from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app import app


class LearningDashboardApiTest(unittest.TestCase):
    client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "version": "0.5.0"})

    def test_known_learner_matches_contract(self) -> None:
        response = self.client.get("/api/learning-summary/xiaoma")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["learner_name"], "小码")
        self.assertEqual(response.json()["completed_hours"], 7.5)

    def test_openapi_exposes_learning_summary_schema(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()["components"]["schemas"]["LearningSummary"]
        self.assertIn("completed_hours", schema["required"])
        self.assertEqual(schema["properties"]["completed_hours"]["type"], "number")

    def test_unknown_learner_is_404(self) -> None:
        response = self.client.get("/api/learning-summary/nobody")
        self.assertEqual(response.status_code, 404)

    def test_invalid_id_is_422(self) -> None:
        response = self.client.get("/api/learning-summary/AA")
        self.assertEqual(response.status_code, 422)

    def test_unavailable_demo_is_503(self) -> None:
        response = self.client.get("/api/demo-unavailable")
        self.assertEqual(response.status_code, 503)

    def test_contract_drift_demo_is_intentionally_wrong(self) -> None:
        response = self.client.get("/api/demo-contract-drift")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()["completed_hours"], str)

    def test_frontend_and_compiled_module_are_served(self) -> None:
        page = self.client.get("/")
        module = self.client.get("/dist/main.js")
        self.assertEqual(page.status_code, 200)
        self.assertIn("学习进度报告器 Web v0.5", page.text)
        self.assertEqual(module.status_code, 200)
        self.assertIn("fetchSummary", module.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
