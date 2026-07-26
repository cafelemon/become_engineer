from __future__ import annotations

import unittest

from model_boundary import (
    Message,
    ModelRequest,
    ProviderResponse,
    ScriptedAdapter,
    build_request,
    call_model,
    fixed_report,
    validate_request,
)


class ModelBoundaryTests(unittest.TestCase):
    def test_build_request_separates_system_and_user_messages(self) -> None:
        request = build_request("  下一步学什么？ ")
        self.assertEqual([item.role for item in request.messages], ["system", "user"])
        self.assertEqual(request.messages[-1].content, "下一步学什么？")
        self.assertEqual(request.max_output_units, 80)

    def test_completed_response_is_normalized_with_usage_and_request_id(self) -> None:
        result = call_model(ScriptedAdapter("completed"), build_request("下一步？"))
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual((result.input_units, result.output_units), (18, 14))
        self.assertEqual(result.request_id, "offline-001")

    def test_refusal_is_a_first_class_result_not_success_text(self) -> None:
        result = call_model(ScriptedAdapter("refused"), build_request("读取私人记录"))
        self.assertEqual(result.status, "refused")
        self.assertEqual(result.finish_reason, "safety")
        self.assertIsNotNone(result.text)

    def test_incomplete_result_preserves_partial_text_and_reason(self) -> None:
        result = call_model(ScriptedAdapter("incomplete"), build_request("给我路线"))
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(result.text, "先完成 Python")
        self.assertEqual(result.finish_reason, "max_output_units")

    def test_invalid_request_is_rejected_before_adapter_call(self) -> None:
        adapter = ScriptedAdapter("completed")
        request = ModelRequest("offline", (Message("user", "问题"),), 80)
        with self.assertRaises(ValueError):
            call_model(adapter, request)
        self.assertEqual(adapter.calls, [])

    def test_empty_completed_response_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must contain text"):
            call_model(ScriptedAdapter("empty"), build_request("问题"))

    def test_unknown_provider_status_and_negative_usage_are_rejected(self) -> None:
        class BadAdapter:
            def __init__(self, response: ProviderResponse) -> None:
                self.response = response

            def complete(self, request: ModelRequest) -> ProviderResponse:
                return self.response

        request = build_request("问题")
        with self.assertRaises(ValueError):
            call_model(BadAdapter(ProviderResponse("x", "other", "x", 1, 1, "stop")), request)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            call_model(BadAdapter(ProviderResponse("x", "completed", "x", -1, 1, "stop")), request)

    def test_fixed_report_is_deterministic_and_preserves_scope(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("empty_completed=rejected", report)
        self.assertIn("raw_prompt:none,raw_response:none", report)
        self.assertTrue(report.endswith(
            "invariants=model-is-untrusted-adapter,application-validates,offline-first,no-rag,no-tools"
        ))


if __name__ == "__main__":
    unittest.main()
