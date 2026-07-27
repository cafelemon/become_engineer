import unittest

from bounded_tool_loop import (
    LoopLimits,
    ModelEvent,
    call,
    fixed_report,
    run_script,
)


class BoundedToolLoopTests(unittest.TestCase):
    def test_tool_then_final_completes_with_bounded_trace(self) -> None:
        result, tools = run_script(
            [
                ModelEvent("tool_calls", elapsed_ms=10, calls=(call(),)),
                ModelEvent("final", elapsed_ms=5, text="private final answer"),
            ]
        )
        self.assertEqual(
            (result.status, result.rounds, result.tool_calls, result.elapsed_ms),
            ("completed", 2, 1, 15),
        )
        self.assertEqual(tools.executed, ["call_status"])
        self.assertNotIn("private final answer", "|".join(result.trace))

    def test_needs_input_stops_without_tools(self) -> None:
        result, tools = run_script([ModelEvent("needs_input", elapsed_ms=2)])
        self.assertEqual(result.status, "needs_input")
        self.assertEqual(tools.executed, [])

    def test_refusal_stops_without_tools(self) -> None:
        result, tools = run_script([ModelEvent("refused", elapsed_ms=2)])
        self.assertEqual(result.status, "refused")
        self.assertEqual(tools.executed, [])

    def test_tool_failure_is_explicit_terminal(self) -> None:
        result, tools = run_script(
            [ModelEvent("tool_calls", calls=(call(),))],
            failures={"call_status": "tool_unavailable"},
        )
        self.assertEqual(result.status, "tool_error")
        self.assertEqual(tools.executed, ["call_status"])

    def test_round_and_call_budgets_stop_before_extra_execution(self) -> None:
        rounds, round_tools = run_script(
            [
                ModelEvent("tool_calls", calls=(call("call_1", step=1),)),
                ModelEvent("tool_calls", calls=(call("call_2", step=2),)),
                ModelEvent("tool_calls", calls=(call("call_3", step=3),)),
                ModelEvent("final", text="too late"),
            ]
        )
        self.assertEqual(rounds.status, "round_budget_exceeded")
        self.assertEqual(round_tools.executed, ["call_1", "call_2", "call_3"])
        calls, call_tools = run_script(
            [
                ModelEvent(
                    "tool_calls",
                    calls=tuple(call(f"call_{index}", slot=index) for index in range(5)),
                )
            ]
        )
        self.assertEqual(calls.status, "call_budget_exceeded")
        self.assertEqual(call_tools.executed, [])

    def test_deadline_stops_before_tool_execution(self) -> None:
        result, tools = run_script(
            [ModelEvent("tool_calls", elapsed_ms=101, calls=(call(),))]
        )
        self.assertEqual(result.status, "deadline_exceeded")
        self.assertEqual(tools.executed, [])

    def test_repeated_semantic_call_is_detected_as_cycle(self) -> None:
        result, tools = run_script(
            [
                ModelEvent("tool_calls", calls=(call("call_first"),)),
                ModelEvent("tool_calls", calls=(call("call_second"),)),
            ]
        )
        self.assertEqual(result.status, "cycle_detected")
        self.assertEqual(tools.executed, ["call_first"])
        changed, changed_tools = run_script(
            [
                ModelEvent("tool_calls", calls=(call("call_first"),)),
                ModelEvent(
                    "tool_calls", calls=(call("call_second", include_recent=True),)
                ),
                ModelEvent("final", text="done"),
            ]
        )
        self.assertEqual(changed.status, "completed")
        self.assertEqual(len(changed_tools.executed), 2)

    def test_fixed_report_lists_every_terminal_and_redacts_content(self) -> None:
        report = fixed_report()
        self.assertIn("max-rounds:3,max-tool-calls:4,deadline-ms:100", report)
        self.assertIn("calls-executed:0,deadline-status:deadline_exceeded", report)
        self.assertIn("cycle=status:cycle_detected,calls-executed:1", report)
        self.assertIn("round_budget_exceeded", report)
        self.assertIn("explicit-terminal", report)
        self.assertNotIn("learner-001", report)


if __name__ == "__main__":
    unittest.main()
