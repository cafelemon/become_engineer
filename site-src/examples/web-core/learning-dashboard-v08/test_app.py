from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import create_app
from database import LearningDatabase


class LearningDashboardFormStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.database_path = self.root / "learning.sqlite3"
        self.database = LearningDatabase(self.database_path)
        self.app = create_app(self.database_path)
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.client.close()
        self.temporary_directory.cleanup()

    def create_session(
        self,
        key: str = "lesson-v08-request-001",
        *,
        hours: float = 1.0,
        note: str = "表单与状态同步练习",
    ):
        return self.client.post(
            "/api/learners/xiaoma/study-sessions",
            headers={"Idempotency-Key": key},
            json={"hours": hours, "note": note},
        )

    def test_health_reports_schema_three(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "version": "0.8.0",
                "storage": "sqlite",
                "schema_version": 3,
            },
        )

    def test_seed_is_idempotent_and_summary_is_aggregated(self) -> None:
        self.database.initialize()
        self.database.initialize()
        self.assertEqual(self.database.session_count("xiaoma"), 3)
        response = self.client.get("/api/learning-summary/xiaoma")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["completed_hours"], 7.5)

    def test_cursor_page_returns_two_rows_and_next_cursor(self) -> None:
        response = self.client.get(
            "/api/learners/xiaoma/study-sessions",
            params={"limit": 2, "after_id": 0},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["session_id"] for item in response.json()["items"]], [1, 2])
        self.assertEqual(response.json()["next_after_id"], 2)

    def test_last_cursor_page_has_no_next_cursor(self) -> None:
        response = self.client.get(
            "/api/learners/xiaoma/study-sessions",
            params={"limit": 2, "after_id": 2},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["session_id"] for item in response.json()["items"]], [3])
        self.assertIsNone(response.json()["next_after_id"])

    def test_list_validates_limit_and_learner(self) -> None:
        invalid_limit = self.client.get(
            "/api/learners/xiaoma/study-sessions",
            params={"limit": 0},
        )
        missing_learner = self.client.get("/api/learners/nobody/study-sessions")
        self.assertEqual(invalid_limit.status_code, 422)
        self.assertEqual(missing_learner.status_code, 404)

    def test_get_returns_one_resource(self) -> None:
        response = self.client.get("/api/study-sessions/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["note"], "HTML 与语义结构")
        self.assertEqual(self.client.get("/api/study-sessions/999").status_code, 404)

    def test_post_replay_returns_same_resource_without_duplicate(self) -> None:
        first = self.create_session()
        second = self.create_session()
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertFalse(first.json()["replayed"])
        self.assertTrue(second.json()["replayed"])
        self.assertEqual(first.headers["location"], f"/api/study-sessions/{first.json()['session']['session_id']}")
        self.assertEqual(
            first.json()["session"]["session_id"],
            second.json()["session"]["session_id"],
        )
        self.assertEqual(self.database.session_count("xiaoma"), 4)

    def test_same_key_with_different_body_is_conflict(self) -> None:
        self.assertEqual(self.create_session().status_code, 201)
        response = self.create_session(hours=2.0, note="另一份内容")
        self.assertEqual(response.status_code, 409)
        self.assertIn("另一份请求内容", response.json()["detail"])
        self.assertEqual(self.database.session_count("xiaoma"), 4)

    def test_post_requires_valid_idempotency_key_and_known_learner(self) -> None:
        missing_header = self.client.post(
            "/api/learners/xiaoma/study-sessions",
            json={"hours": 1.0, "note": "没有请求键"},
        )
        short_header = self.client.post(
            "/api/learners/xiaoma/study-sessions",
            headers={"Idempotency-Key": "short"},
            json={"hours": 1.0, "note": "请求键太短"},
        )
        unknown = self.client.post(
            "/api/learners/nobody/study-sessions",
            headers={"Idempotency-Key": "lesson-v07-unknown"},
            json={"hours": 1.0, "note": "学习者不存在"},
        )
        self.assertEqual(missing_header.status_code, 422)
        self.assertEqual(short_header.status_code, 422)
        self.assertEqual(unknown.status_code, 404)

    def test_server_validation_identifies_form_fields(self) -> None:
        invalid_hours = self.client.post(
            "/api/learners/xiaoma/study-sessions",
            headers={"Idempotency-Key": "lesson-v08-invalid-hours"},
            json={"hours": 0.3, "note": "步长不对"},
        )
        invalid_note = self.client.post(
            "/api/learners/xiaoma/study-sessions",
            headers={"Idempotency-Key": "lesson-v08-invalid-note"},
            json={"hours": 1.0, "note": "   "},
        )
        self.assertEqual(invalid_hours.status_code, 422)
        self.assertEqual(invalid_note.status_code, 422)
        self.assertIn("hours", [item["loc"][-1] for item in invalid_hours.json()["detail"]])
        self.assertIn("note", [item["loc"][-1] for item in invalid_note.json()["detail"]])

    def test_put_replaces_resource_and_is_repeatable(self) -> None:
        payload = {"hours": 1.25, "note": "改成复盘 REST"}
        first = self.client.put("/api/study-sessions/1", json=payload)
        second = self.client.put("/api/study-sessions/1", json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json(), second.json())
        self.assertEqual(self.database.get_session(1).hours, 1.25)

    def test_put_validates_body_and_missing_resource(self) -> None:
        invalid = self.client.put(
            "/api/study-sessions/1",
            json={"hours": -1, "note": "无效"},
        )
        missing = self.client.put(
            "/api/study-sessions/999",
            json={"hours": 1, "note": "不存在"},
        )
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(missing.status_code, 404)

    def test_delete_is_final_state_idempotent(self) -> None:
        first = self.client.delete("/api/study-sessions/1")
        second = self.client.delete("/api/study-sessions/1")
        self.assertEqual(first.status_code, 204)
        self.assertEqual(second.status_code, 404)
        self.assertEqual(self.client.get("/api/study-sessions/1").status_code, 404)

    def test_created_resource_persists_in_new_database_instance(self) -> None:
        response = self.create_session("lesson-v08-restart")
        session_id = response.json()["session"]["session_id"]
        reopened = LearningDatabase(self.database_path)
        self.assertEqual(reopened.get_session(session_id).note, "表单与状态同步练习")
        self.assertEqual(reopened.get_summary("xiaoma").completed_hours, 8.5)

    def test_database_constraints_and_foreign_keys_still_apply(self) -> None:
        self.database.initialize()
        connection = self.database.connect()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO study_sessions(learner_id, hours, note) VALUES (?, ?, ?)",
                    ("ghost", 1.0, "不存在的学习者"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO study_sessions(learner_id, hours, note) VALUES (?, ?, ?)",
                    ("xiaoma", 0.3, "小时步长错误"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO study_sessions(learner_id, hours, note) VALUES (?, ?, ?)",
                    ("xiaoma", 1.0, "   "),
                )
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        finally:
            connection.close()

    def test_openapi_lists_rest_resources(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        self.assertIn("/api/learners/{learner_id}/study-sessions", paths)
        self.assertIn("post", paths["/api/learners/{learner_id}/study-sessions"])
        self.assertIn("/api/study-sessions/{session_id}", paths)
        self.assertIn("put", paths["/api/study-sessions/{session_id}"])
        self.assertIn("delete", paths["/api/study-sessions/{session_id}"])

    def test_static_dashboard_is_served(self) -> None:
        page = self.client.get("/")
        css = self.client.get("/styles.css")
        self.assertEqual(page.status_code, 200)
        self.assertIn("学习进度报告器 Web v0.8", page.text)
        self.assertIn("data-session-form", page.text)
        self.assertEqual(css.status_code, 200)


if __name__ == "__main__":
    unittest.main()
