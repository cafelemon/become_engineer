from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import create_app
from database import LearningDatabase


class LearningDashboardPersistenceTest(unittest.TestCase):
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

    def test_health_reports_sqlite_schema(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "version": "0.6.0",
                "storage": "sqlite",
                "schema_version": 1,
            },
        )

    def test_seed_is_idempotent(self) -> None:
        self.database.initialize()
        self.database.initialize()
        self.assertEqual(self.database.session_count("xiaoma"), 1)
        self.assertEqual(self.database.get_summary("xiaoma").completed_hours, 7.5)

    def test_known_learner_is_aggregated_from_sessions(self) -> None:
        response = self.client.get("/api/learning-summary/xiaoma")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["learner_name"], "小码")
        self.assertEqual(response.json()["completed_hours"], 7.5)

    def test_created_session_persists_across_database_instances(self) -> None:
        response = self.client.post(
            "/api/study-sessions",
            json={
                "learner_id": "xiaoma",
                "hours": 1.25,
                "note": "服务重启前保存",
            },
        )
        self.assertEqual(response.status_code, 201)

        reopened = LearningDatabase(self.database_path)
        self.assertEqual(reopened.get_summary("xiaoma").completed_hours, 8.75)
        self.assertEqual(reopened.session_count("xiaoma"), 2)

    def test_unknown_learner_is_404(self) -> None:
        read_response = self.client.get("/api/learning-summary/nobody")
        write_response = self.client.post(
            "/api/study-sessions",
            json={"learner_id": "nobody", "hours": 1, "note": "不存在"},
        )
        self.assertEqual(read_response.status_code, 404)
        self.assertEqual(write_response.status_code, 404)

    def test_invalid_hours_are_rejected_before_sql(self) -> None:
        zero = self.client.post(
            "/api/study-sessions",
            json={"learner_id": "xiaoma", "hours": 0, "note": "错误"},
        )
        too_large = self.client.post(
            "/api/study-sessions",
            json={"learner_id": "xiaoma", "hours": 25, "note": "错误"},
        )
        self.assertEqual(zero.status_code, 422)
        self.assertEqual(too_large.status_code, 422)
        self.assertEqual(self.database.session_count("xiaoma"), 1)

    def test_database_constraints_reject_invalid_rows(self) -> None:
        self.database.initialize()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "INSERT INTO study_sessions(learner_id, hours, note) VALUES (?, ?, ?)",
                    ("xiaoma", -1, "数据库也会拒绝"),
                )

        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "INSERT INTO study_sessions(learner_id, hours, note) VALUES (?, ?, ?)",
                    ("ghost", 1, "外键会拒绝"),
                )

    def test_placeholder_stores_sql_like_text_as_data(self) -> None:
        note = "'); DROP TABLE learners; --"
        response = self.client.post(
            "/api/study-sessions",
            json={"learner_id": "xiaoma", "hours": 0.5, "note": note},
        )
        self.assertEqual(response.status_code, 201)

        connection = self.database.connect()
        try:
            stored = connection.execute(
                "SELECT note FROM study_sessions WHERE id = ?",
                (response.json()["session_id"],),
            ).fetchone()
            learners = connection.execute("SELECT COUNT(*) FROM learners").fetchone()
        finally:
            connection.close()

        self.assertEqual(stored["note"], note)
        self.assertEqual(learners[0], 2)

    def test_transaction_rolls_back_all_changes_after_failure(self) -> None:
        self.database.initialize()
        before = self.database.session_count("xiaoma")

        with self.assertRaises(sqlite3.OperationalError):
            with self.database.transaction() as connection:
                connection.execute(
                    "INSERT INTO study_sessions(learner_id, hours, note) VALUES (?, ?, ?)",
                    ("xiaoma", 2, "应该被回滚"),
                )
                connection.execute("INSERT INTO table_that_does_not_exist VALUES (1)")

        self.assertEqual(self.database.session_count("xiaoma"), before)

    def test_unopenable_database_is_a_readable_503(self) -> None:
        bad_path = self.root / "not-a-database"
        bad_path.mkdir()
        bad_client = TestClient(create_app(bad_path))
        try:
            response = bad_client.get("/api/health")
        finally:
            bad_client.close()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "数据库暂时不可用")

    def test_openapi_exposes_read_and_append_contracts(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        document = response.json()
        self.assertIn("/api/learning-summary/{learner_id}", document["paths"])
        self.assertIn("/api/study-sessions", document["paths"])
        session_schema = document["components"]["schemas"]["StudySessionInput"]
        self.assertIn("hours", session_schema["required"])

    def test_frontend_and_compiled_module_are_served(self) -> None:
        page = self.client.get("/")
        module = self.client.get("/dist/main.js")
        self.assertEqual(page.status_code, 200)
        self.assertIn("学习进度报告器 Web v0.6", page.text)
        self.assertIn("保存 1 小时", page.text)
        self.assertEqual(module.status_code, 200)
        self.assertIn("saveStudySession", module.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
