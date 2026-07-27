from dataclasses import replace
import unittest

from tool_workflow_eval import (
    EvaluationReport,
    evaluate,
    fixed_cases,
    fixed_report,
    protocol_fingerprint,
    regression_gate,
)


class ToolWorkflowEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = fixed_cases()
        self.report = evaluate(self.cases)

    def test_protocol_fingerprint_is_order_independent_but_content_sensitive(self) -> None:
        self.assertEqual(
            protocol_fingerprint(self.cases),
            protocol_fingerprint(tuple(reversed(self.cases))),
        )
        changed = list(self.cases)
        changed[0] = replace(changed[0], expected_tool_calls=2)
        self.assertNotEqual(
            protocol_fingerprint(self.cases), protocol_fingerprint(changed)
        )

    def test_all_case_outcomes_and_handler_counts_match(self) -> None:
        self.assertEqual(self.report.case_count, 8)
        self.assertTrue(all(case.outcome_correct for case in self.report.cases))
        self.assertEqual(self.report.metrics["outcome_accuracy"], 1.0)

    def test_benign_outcomes_are_scored_on_their_own_denominator(self) -> None:
        benign = [case for case in self.report.cases if case.category == "benign"]
        self.assertEqual(len(benign), 2)
        self.assertEqual(self.report.metrics["benign_outcome_accuracy"], 1.0)

    def test_safety_cases_reject_without_unsafe_execution(self) -> None:
        safety = [case for case in self.report.cases if case.category == "safety"]
        self.assertEqual(len(safety), 3)
        self.assertTrue(all(case.safety_rejection_correct for case in safety))
        self.assertEqual(self.report.metrics["safety_rejection_accuracy"], 1.0)
        self.assertEqual(self.report.unsafe_executions, 0)

    def test_budget_cases_stop_with_exact_call_accounting(self) -> None:
        budgets = [case for case in self.report.cases if case.category == "budget"]
        self.assertEqual(
            [case.status for case in budgets],
            ["cycle_detected", "call_budget_exceeded", "deadline_exceeded"],
        )
        self.assertTrue(all(case.budget_compliant for case in budgets))
        self.assertEqual(self.report.metrics["budget_compliance"], 1.0)
        self.assertEqual(self.report.metrics["call_accounting_accuracy"], 1.0)

    def test_regression_gate_passes_baseline_and_blocks_metric_drop(self) -> None:
        self.assertEqual(regression_gate(self.report, self.report), (True, "passed"))
        metrics = dict(self.report.metrics)
        metrics["safety_rejection_accuracy"] = 2 / 3
        regressed = replace(self.report, metrics=metrics, passed=False)
        self.assertEqual(
            regression_gate(self.report, regressed),
            (False, "regressed:safety_rejection_accuracy"),
        )

    def test_regression_gate_rejects_incompatible_protocol(self) -> None:
        incompatible = replace(self.report, protocol_fingerprint="different")
        self.assertEqual(
            regression_gate(self.report, incompatible),
            (False, "incompatible_protocol"),
        )

    def test_fixed_report_is_complete_and_redacted(self) -> None:
        report = fixed_report()
        self.assertIn("case-mix=benign:2,safety:3,budget:3", report)
        self.assertIn("unsafe-executions:0", report)
        self.assertIn("gate=passed:true,reason:passed", report)
        self.assertIn("eight-cases-not-production-quality", report)
        for secret in ["learner-001", "run_shell", "weekly_minutes", '"cmd"']:
            self.assertNotIn(secret, report)


if __name__ == "__main__":
    unittest.main()
