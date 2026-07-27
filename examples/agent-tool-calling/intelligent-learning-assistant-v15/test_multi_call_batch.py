import unittest

from multi_call_batch import (
    BatchProtocolError,
    CandidateCall,
    MAX_CALLS,
    SequentialToolExecutor,
    ToolOutput,
    assemble_outputs,
    demo_calls,
    demo_executor,
    fixed_report,
    outputs_json,
    validate_batch,
)


class MultiCallBatchTests(unittest.TestCase):
    def test_batch_requires_one_to_four_calls(self) -> None:
        with self.assertRaisesRegex(BatchProtocolError, "at least one"):
            validate_batch([])
        too_many = [
            CandidateCall(f"call_{index}", "known", {}) for index in range(MAX_CALLS + 1)
        ]
        with self.assertRaisesRegex(BatchProtocolError, "budget"):
            validate_batch(too_many)

    def test_duplicate_or_invalid_call_id_stops_before_handlers(self) -> None:
        executor = demo_executor()
        duplicate = (
            CandidateCall("call_same", "get_learning_status", {}),
            CandidateCall("call_same", "get_course_outline", {}),
        )
        with self.assertRaisesRegex(BatchProtocolError, "unique"):
            executor.execute_batch(duplicate)
        with self.assertRaisesRegex(BatchProtocolError, "invalid"):
            executor.execute_batch((CandidateCall("bad id", "known", {}),))
        self.assertEqual(executor.handler_calls, [])

    def test_sequential_execution_preserves_model_order(self) -> None:
        calls = demo_calls()
        executor = demo_executor()
        outputs = executor.execute_batch(calls)
        self.assertEqual(
            [output.call_id for output in outputs],
            ["call_status", "call_outline", "call_unknown"],
        )
        self.assertEqual(executor.handler_calls, ["call_status", "call_outline"])

    def test_out_of_order_results_are_restored_by_call_id(self) -> None:
        calls = demo_calls()[:2]
        reversed_outputs = (
            ToolOutput("call_outline", "get_course_outline", "ok", {"lesson_count": 6}),
            ToolOutput("call_status", "get_learning_status", "ok", {"completed_count": 4}),
        )
        restored = assemble_outputs(calls, reversed_outputs)
        self.assertEqual([item.call_id for item in restored], ["call_status", "call_outline"])

    def test_missing_extra_and_duplicate_outputs_are_rejected(self) -> None:
        calls = demo_calls()[:2]
        one = ToolOutput("call_status", "get_learning_status", "ok", {"count": 4})
        with self.assertRaisesRegex(BatchProtocolError, "no output"):
            assemble_outputs(calls, [one])
        extra = ToolOutput("call_extra", "get_course_outline", "ok", {"count": 1})
        with self.assertRaisesRegex(BatchProtocolError, "no matching"):
            assemble_outputs(calls[:1], [one, extra])
        with self.assertRaisesRegex(BatchProtocolError, "exactly one"):
            assemble_outputs(calls, [one, one])

    def test_tool_name_mismatch_is_rejected(self) -> None:
        call = demo_calls()[0]
        output = ToolOutput(call.call_id, "get_course_outline", "ok", {"count": 1})
        with self.assertRaisesRegex(BatchProtocolError, "does not match"):
            assemble_outputs([call], [output])

    def test_partial_failure_does_not_discard_successes(self) -> None:
        outputs = demo_executor().execute_batch(demo_calls())
        self.assertEqual([item.status for item in outputs], ["ok", "ok", "error"])
        self.assertEqual(outputs[2].error_code, "unknown_tool")
        payload = outputs_json(outputs)
        self.assertIn('"call_id":"call_status"', payload)
        self.assertIn('"error_code":"unknown_tool"', payload)

    def test_fixed_report_proves_correlation_and_isolation(self) -> None:
        report = fixed_report()
        self.assertIn("calls:3,max:4,unique-call-ids:true", report)
        self.assertIn("out-of-order-restored:true", report)
        self.assertIn("successes:2,errors:1,batch-aborted:false", report)
        self.assertIn("call-id-not-index", report)
        self.assertNotIn("learner-001", report)


if __name__ == "__main__":
    unittest.main()
