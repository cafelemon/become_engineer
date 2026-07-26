from __future__ import annotations

import unittest

from recovery_policy import (
    AttemptOutcome,
    RetryPolicy,
    ScriptedAdapter,
    VirtualClock,
    fixed_report,
    run_with_recovery,
)


class RecoveryPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = RetryPolicy(3, 100, 500, (50, 100))

    def run_script(
        self,
        outcomes: list[AttemptOutcome],
        policy: RetryPolicy | None = None,
    ):
        clock = VirtualClock()
        adapter = ScriptedAdapter(outcomes, clock)
        result = run_with_recovery(adapter, policy or self.policy, clock)
        return result, adapter

    def test_transient_failures_retry_then_complete(self) -> None:
        result, adapter = self.run_script([
            AttemptOutcome("unavailable", 30),
            AttemptOutcome("rate_limited", 30),
            AttemptOutcome("completed", 40, "ready"),
        ])
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.text, "ready")
        self.assertEqual(adapter.calls, 3)
        self.assertEqual(result.elapsed_ms, 250)
        self.assertEqual([r.next_backoff_ms for r in result.attempts], [50, 100, None])

    def test_authentication_failure_is_never_retried(self) -> None:
        result, adapter = self.run_script([
            AttemptOutcome("authentication_failed", 20),
            AttemptOutcome("completed", 10, "must not run"),
        ])
        self.assertEqual(result.terminal_code, "authentication_failed")
        self.assertEqual(adapter.calls, 1)

    def test_refusal_and_invalid_output_are_terminal(self) -> None:
        for code in ["refused", "invalid_output", "missing_information"]:
            with self.subTest(code=code):
                result, adapter = self.run_script([AttemptOutcome(code, 5)])
                self.assertEqual(result.terminal_code, code)
                self.assertEqual(adapter.calls, 1)

    def test_attempt_timeout_is_retryable_but_bounded(self) -> None:
        result, _ = self.run_script([
            AttemptOutcome("completed", 150, "too late"),
            AttemptOutcome("completed", 20, "second"),
        ])
        self.assertEqual([r.outcome for r in result.attempts], ["timeout", "completed"])
        self.assertEqual(result.elapsed_ms, 170)

    def test_overall_deadline_stops_inside_later_attempt(self) -> None:
        result, adapter = self.run_script(
            [
                AttemptOutcome("unavailable", 80),
                AttemptOutcome("unavailable", 80),
                AttemptOutcome("completed", 1, "too late"),
            ],
            RetryPolicy(3, 100, 200, (60, 60)),
        )
        self.assertEqual(result.terminal_code, "deadline_exceeded")
        self.assertEqual(result.elapsed_ms, 200)
        self.assertEqual(adapter.calls, 2)

    def test_backoff_that_would_reach_deadline_is_not_slept(self) -> None:
        result, adapter = self.run_script(
            [AttemptOutcome("unavailable", 80), AttemptOutcome("completed", 1, "late")],
            RetryPolicy(2, 100, 100, (20,)),
        )
        self.assertEqual(result.terminal_code, "deadline_exceeded")
        self.assertEqual(result.elapsed_ms, 80)
        self.assertEqual(adapter.calls, 1)

    def test_attempt_budget_is_a_hard_cap(self) -> None:
        result, adapter = self.run_script([
            AttemptOutcome("unavailable", 1),
            AttemptOutcome("rate_limited", 1),
            AttemptOutcome("timeout", 1),
            AttemptOutcome("completed", 1, "fourth"),
        ])
        self.assertEqual(result.terminal_code, "attempt_budget_exhausted")
        self.assertEqual(adapter.calls, 3)

    def test_fixed_report_is_deterministic_and_redacted(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("attempts:3,codes:unavailable>rate_limited>completed", report)
        self.assertIn("terminal:deadline_exceeded", report)
        self.assertTrue(report.endswith(
            "invariants=retry-transient-only,never-past-deadline,never-unbounded,no-rag,no-tools"
        ))


if __name__ == "__main__":
    unittest.main()
