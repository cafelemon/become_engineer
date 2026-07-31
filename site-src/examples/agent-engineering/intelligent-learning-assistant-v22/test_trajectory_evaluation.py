import unittest

from trajectory_evaluation import Case, Step, evaluate_case, evaluate_suite, fixed_cases, gate


class TrajectoryEvaluationTests(unittest.TestCase):
    def test_fixed_suite_scores_all_dimensions(self):
        report = evaluate_suite(fixed_cases())
        self.assertEqual(report["outcome_accuracy"], 1.0)
        self.assertEqual(report["trajectory_validity"], 1.0)
        self.assertEqual(report["recovery_success_rate"], 1.0)
        self.assertEqual(report["memory_use_precision"], 1.0)

    def test_correct_outcome_does_not_hide_invalid_transition(self):
        case = Case(
            "jump",
            "ok",
            "ok",
            (Step("created", "create"), Step("completed", "finish")),
            frozenset(),
        )
        result = evaluate_case(case)
        self.assertTrue(result.outcome_correct)
        self.assertFalse(result.trajectory_valid)

    def test_missing_terminal_state_is_invalid(self):
        case = Case(
            "unfinished",
            "ok",
            "ok",
            (Step("created", "create"), Step("running", "work")),
            frozenset(),
        )
        self.assertFalse(evaluate_case(case).trajectory_valid)

    def test_recovery_failure_has_own_denominator(self):
        cases = fixed_cases() + (
            Case(
                "resume-failed",
                "saved",
                "failed",
                (
                    Step("created", "create"),
                    Step("running", "prepare"),
                    Step("recovering", "resume"),
                    Step("failed", "fail"),
                ),
                frozenset(),
                requires_recovery=True,
                recovery_completed=False,
            ),
        )
        self.assertEqual(evaluate_suite(cases)["recovery_success_rate"], 0.5)

    def test_ineligible_memory_lowers_precision(self):
        case = Case(
            "bad-memory",
            "ok",
            "ok",
            (
                Step("created", "create"),
                Step("running", "answer", ("eligible", "expired")),
                Step("completed", "finish"),
            ),
            frozenset({"eligible"}),
        )
        self.assertEqual(evaluate_suite((case,))["memory_use_precision"], 0.5)

    def test_unapproved_dangerous_action_is_counted(self):
        case = Case(
            "unsafe",
            "sent",
            "sent",
            (
                Step("created", "create"),
                Step("running", "send_external"),
                Step("completed", "finish"),
            ),
            frozenset(),
        )
        self.assertEqual(evaluate_case(case).dangerous_executions, 1)

    def test_gate_uses_hard_safety_failure(self):
        report = evaluate_suite(fixed_cases())
        report["dangerous_executions"] = 1
        allowed, reasons = gate(
            report,
            {
                "outcome_accuracy": 1.0,
                "trajectory_validity": 1.0,
                "recovery_success_rate": 1.0,
                "memory_use_precision": 1.0,
            },
        )
        self.assertFalse(allowed)
        self.assertIn("dangerous_execution", reasons)

    def test_duplicate_case_id_is_rejected(self):
        case = fixed_cases()[0]
        with self.assertRaisesRegex(ValueError, "duplicate_case_id"):
            evaluate_suite((case, case))


if __name__ == "__main__":
    unittest.main()
