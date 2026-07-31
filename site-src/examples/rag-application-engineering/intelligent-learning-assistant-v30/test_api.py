import unittest

from fastapi.testclient import TestClient

from app import create_app
from knowledge_service import KnowledgeService


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.service = KnowledgeService()
        self.client = TestClient(create_app(self.service))
        self.headers = {"X-Subject-ID": "alice"}

    def test_anonymous_is_401(self):
        response = self.client.post("/api/knowledge-sources", json={"name": "guide"})
        self.assertEqual(401, response.status_code)
        self.assertEqual("Subject", response.headers["www-authenticate"])

    def test_end_to_end_upload_debug_chat(self):
        source = self.client.post("/api/knowledge-sources", headers=self.headers, json={"name": "guide"}).json()
        uploaded = self.client.post(
            f"/api/knowledge-sources/{source['source_id']}/versions", headers=self.headers,
            json={"kind": "markdown", "content": "ACL 必须在召回前执行。"},
        )
        self.assertEqual(202, uploaded.status_code)
        session = self.client.post("/api/chat/sessions", headers=self.headers).json()
        answer = self.client.post(
            f"/api/chat/sessions/{session['session_id']}/messages", headers=self.headers, json={"question": "ACL"}
        )
        self.assertEqual(201, answer.status_code)
        self.assertEqual(1, len(answer.json()["citations"]))

    def test_other_owner_gets_resource_hiding_404(self):
        source = self.client.post("/api/knowledge-sources", headers=self.headers, json={"name": "guide"}).json()
        response = self.client.get(f"/api/knowledge-sources/{source['source_id']}/versions", headers={"X-Subject-ID": "bob"})
        self.assertEqual(404, response.status_code)

    def test_health_metrics_and_html(self):
        self.assertEqual("live", self.client.get("/health/live").json()["status"])
        self.assertEqual("ready", self.client.get("/health/ready").json()["status"])
        self.assertIn("rag_requests_total", self.client.get("/metrics").text)
        html = self.client.get("/").text
        self.assertIn("文档管理台", html)
        self.assertIn("<noscript>", html)


if __name__ == "__main__":
    unittest.main()
