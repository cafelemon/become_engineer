from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app import app


class LearningDashboardApiTest(unittest.TestCase):
    client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "version": "0.4.0"})

    def test_known_learner_matches_contract(self) -> None:
        response = self.client.get("/api/learning-summary/xiaoma")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["learner_name"], "小码")
        self.assertEqual(response.json()["completed_lessons"], 7)
        self.assertEqual(response.json()["status"], "按计划推进")

    def test_unknown_learner_is_404(self) -> None:
        response = self.client.get("/api/learning-summary/nobody")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "没有找到这位学习者")

    def test_invalid_id_is_422(self) -> None:
        response = self.client.get("/api/learning-summary/AA")
        self.assertEqual(response.status_code, 422)

    def test_unavailable_demo_is_503(self) -> None:
        response = self.client.get("/api/demo-unavailable")
        self.assertEqual(response.status_code, 503)

    def test_frontend_is_served_by_same_app(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("学习进度报告器 Web v0.4", response.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
