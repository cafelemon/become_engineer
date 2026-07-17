from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app import app


class LearningApiTest(unittest.TestCase):
    client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_known_learner(self) -> None:
        response = self.client.get("/api/learning-summary/xiaoma")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["learner_name"], "小码")
        self.assertEqual(response.json()["status"], "按计划推进")

    def test_unknown_learner(self) -> None:
        response = self.client.get("/api/learning-summary/nobody")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "没有找到这位学习者")

    def test_invalid_learner_id(self) -> None:
        response = self.client.get("/api/learning-summary/AA")
        self.assertEqual(response.status_code, 422)

    def test_cors_is_limited_to_review_origin(self) -> None:
        allowed = self.client.get(
            "/api/health", headers={"Origin": "http://127.0.0.1:8768"}
        )
        denied = self.client.get(
            "/api/health", headers={"Origin": "https://example.com"}
        )
        self.assertEqual(
            allowed.headers.get("access-control-allow-origin"),
            "http://127.0.0.1:8768",
        )
        self.assertIsNone(denied.headers.get("access-control-allow-origin"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
