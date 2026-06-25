from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from safe_sales import (  # noqa: E402
    ToolValidationError,
    connect_read_only,
    execute_tool_call,
    get_monthly_sales,
    initialize_demo_database,
    run_offline_tool_call,
)
from openai_adapter import run_with_openai  # noqa: E402


class SafeSalesToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_directory.name) / "sales.db"
        initialize_demo_database(self.db_path)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_monthly_summary(self) -> None:
        result = get_monthly_sales(
            self.db_path,
            year=2025,
            month=1,
            product_name=None,
        )
        self.assertEqual(result["total_units"], 6)
        self.assertEqual(result["total_revenue_cents"], 119400)
        self.assertEqual([item["product_name"] for item in result["items"]], [
            "Keyboard",
            "Mouse",
        ])

    def test_product_filter(self) -> None:
        result = get_monthly_sales(
            self.db_path,
            year=2025,
            month=1,
            product_name="Keyboard",
        )
        self.assertEqual(result["total_units"], 3)
        self.assertEqual(result["total_revenue_cents"], 89700)

    def test_empty_result_is_successful(self) -> None:
        result = get_monthly_sales(
            self.db_path,
            year=2026,
            month=1,
            product_name=None,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["items"], [])
        self.assertEqual(result["total_revenue_cents"], 0)

    def test_invalid_month_is_rejected(self) -> None:
        with self.assertRaisesRegex(ToolValidationError, "month"):
            get_monthly_sales(
                self.db_path,
                year=2025,
                month=13,
                product_name=None,
            )

    def test_unknown_tool_is_rejected(self) -> None:
        with self.assertRaisesRegex(ToolValidationError, "unknown tool"):
            execute_tool_call(
                self.db_path,
                name="execute_sql",
                arguments={"year": 2025, "month": 1, "product_name": None},
            )

    def test_extra_argument_is_rejected(self) -> None:
        with self.assertRaisesRegex(ToolValidationError, "unexpected"):
            execute_tool_call(
                self.db_path,
                name="get_monthly_sales",
                arguments={
                    "year": 2025,
                    "month": 1,
                    "product_name": None,
                    "sql": "DROP TABLE sales",
                },
            )

    def test_injection_style_product_is_only_a_value(self) -> None:
        malicious_name = "Keyboard'; DROP TABLE sales; --"
        result = get_monthly_sales(
            self.db_path,
            year=2025,
            month=1,
            product_name=malicious_name,
        )
        self.assertEqual(result["items"], [])

        normal_result = get_monthly_sales(
            self.db_path,
            year=2025,
            month=1,
            product_name="Keyboard",
        )
        self.assertEqual(normal_result["total_units"], 3)

    def test_database_connection_is_read_only(self) -> None:
        with connect_read_only(self.db_path) as connection:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("DELETE FROM sales")

    def test_offline_trace_keeps_call_id(self) -> None:
        trace = run_offline_tool_call(
            self.db_path,
            year=2025,
            month=1,
            product_name="Keyboard",
        )
        call = trace["function_call"]
        output = trace["function_call_output"]
        self.assertEqual(call["call_id"], output["call_id"])
        self.assertEqual(
            json.loads(output["output"])["total_revenue_cents"],
            89700,
        )

    def test_openai_adapter_requires_api_key(self) -> None:
        clean_environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"OPENAI_API_KEY", "OPENAI_MODEL"}
        }
        with patch.dict(os.environ, clean_environment, clear=True):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                run_with_openai("Show January sales", self.db_path)


if __name__ == "__main__":
    unittest.main()
