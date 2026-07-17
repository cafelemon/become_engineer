from __future__ import annotations

import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agent_tool import TOOLS, TOOL_NAME, ToolCallError, execute_tool, load_catalog, offline_run
from shared.deepseek_client import request_tool_call


class AgentToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = load_catalog()

    def test_known_course(self) -> None:
        result = execute_tool(TOOL_NAME, '{"course_id":"python-basics-01"}', self.catalog)
        self.assertEqual(result["title"], "变量、基本类型与输入输出")

    def test_offline_trace_keeps_call_id(self) -> None:
        trace = offline_run("cs-core-19")
        self.assertEqual(trace["tool_call"]["id"], "call_offline_001")
        self.assertIn("BFS", trace["answer"])

    def test_unknown_tool_is_rejected(self) -> None:
        with self.assertRaises(ToolCallError):
            execute_tool("read_file", '{"course_id":"python-basics-01"}', self.catalog)

    def test_extra_arguments_are_rejected(self) -> None:
        arguments = json.dumps({"course_id": "python-basics-01", "path": "/etc/passwd"})
        with self.assertRaises(ToolCallError):
            execute_tool(TOOL_NAME, arguments, self.catalog)

    def test_invalid_and_unknown_ids_are_rejected(self) -> None:
        for course_id in ["../secret", "AA", "not-built-99"]:
            with self.subTest(course_id=course_id), self.assertRaises(ToolCallError):
                execute_tool(TOOL_NAME, json.dumps({"course_id": course_id}), self.catalog)

    def test_catalog_is_not_modified(self) -> None:
        before = json.dumps(self.catalog, ensure_ascii=False, sort_keys=True)
        execute_tool(TOOL_NAME, '{"course_id":"python-basics-01"}', self.catalog)
        after = json.dumps(self.catalog, ensure_ascii=False, sort_keys=True)
        self.assertEqual(before, after)

    def test_live_request_allows_model_to_propose_the_registered_tool(self) -> None:
        captured: dict[str, object] = {}

        def create(**kwargs: object) -> object:
            captured.update(kwargs)
            tool_call = SimpleNamespace(
                id="call_test_001",
                function=SimpleNamespace(
                    name=TOOL_NAME,
                    arguments='{"course_id":"python-basics-01"}',
                ),
            )
            message = SimpleNamespace(tool_calls=[tool_call])
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )
        with patch("shared.deepseek_client._client", return_value=(client, "test-model")):
            call, _message, _model = request_tool_call(
                [{"role": "user", "content": "查课程状态"}], TOOLS
            )

        self.assertEqual(call["name"], TOOL_NAME)
        self.assertEqual(captured["tool_choice"], "auto")


if __name__ == "__main__":
    unittest.main(verbosity=2)
