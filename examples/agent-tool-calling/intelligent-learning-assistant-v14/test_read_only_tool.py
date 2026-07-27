from pathlib import Path
import sqlite3
import tempfile
import unittest

from read_only_tool import (
    LearningStatusReader,
    Principal,
    ReadOnlyToolExecutor,
    ValidatedToolCall,
    fixed_report,
    seed_database,
)


class ReadOnlyToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "learning.db"
        seed_database(self.database)
        self.reader = LearningStatusReader(self.database)
        self.executor = ReadOnlyToolExecutor(self.reader)
        self.principal = Principal(
            "learner-001", frozenset({"learning_status:read"})
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def call(self, **overrides):
        arguments = {"learner_id": "learner-001", "include_recent": True}
        arguments.update(overrides.pop("arguments", {}))
        return ValidatedToolCall(
            overrides.pop("call_id", "call_read1"),
            overrides.pop("name", "get_learning_status"),
            arguments,
        )

    def test_owner_with_permission_reads_bounded_status(self) -> None:
        result = self.executor.execute(self.call(), self.principal)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.data["completed_count"], 4)
        self.assertEqual(
            result.data["recent_course_ids"],
            ["agent-tool-calling-01", "llm-rag-eval-06", "llm-use-06"],
        )
        self.assertEqual(self.reader.handler_calls, 1)

    def test_missing_permission_denies_before_handler(self) -> None:
        result = self.executor.execute(
            self.call(), Principal("learner-001", frozenset())
        )
        self.assertEqual((result.status, result.error_code), ("error", "forbidden"))
        self.assertEqual(self.reader.handler_calls, 0)

    def test_cross_learner_access_denies_before_handler(self) -> None:
        result = self.executor.execute(
            self.call(arguments={"learner_id": "learner-002"}), self.principal
        )
        self.assertEqual(result.error_code, "forbidden")
        self.assertEqual(self.reader.handler_calls, 0)

    def test_invalid_business_values_do_not_reach_handler(self) -> None:
        for arguments in [
            {"learner_id": "learner-001' OR 1=1 --"},
            {"learner_id": "../learner-001"},
            {"include_recent": 1},
            {"admin": True},
        ]:
            with self.subTest(arguments=arguments):
                result = self.executor.execute(self.call(arguments=arguments), self.principal)
                self.assertEqual(result.error_code, "invalid_arguments")
        self.assertEqual(self.reader.handler_calls, 0)

    def test_unknown_tool_does_not_reach_handler(self) -> None:
        result = self.executor.execute(self.call(name="execute_sql"), self.principal)
        self.assertEqual(result.error_code, "unknown_tool")
        self.assertEqual(self.reader.handler_calls, 0)

    def test_database_connection_is_really_read_only(self) -> None:
        connection = self.reader._connect_read_only()
        try:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute(
                    "INSERT INTO learning_status VALUES(?,?,?)",
                    ("learner-001", "forbidden-write", "2026-07-26T00:00:00Z"),
                )
        finally:
            connection.close()

    def test_result_envelope_is_stable_and_does_not_leak_exception(self) -> None:
        result = self.executor.execute(self.call(), self.principal)
        payload = result.to_json()
        self.assertIn('"call_id":"call_read1"', payload)
        self.assertIn('"status":"ok"', payload)
        self.assertNotIn(str(self.database), payload)
        denied = self.executor.execute(
            self.call(arguments={"learner_id": "learner-002"}), self.principal
        )
        self.assertIn('"data":null', denied.to_json())
        self.assertIn('"error_code":"forbidden"', denied.to_json())

    def test_fixed_report_proves_authorization_and_read_only_boundary(self) -> None:
        report = fixed_report()
        self.assertIn("status:ok,completed:4,recent:3", report)
        self.assertIn("error:forbidden,handler-called:false", report)
        self.assertIn("sqlite-uri:mode=ro,sql:parameterized,result-limit:3", report)
        self.assertIn("authorize-before-handler", report)


if __name__ == "__main__":
    unittest.main()
