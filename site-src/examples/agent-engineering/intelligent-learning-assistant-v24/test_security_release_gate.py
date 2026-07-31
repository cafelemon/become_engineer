import unittest

from security_release_gate import Event, attack_fixtures, authorize, release_gate, run_suite


class SecurityReleaseGateTests(unittest.TestCase):
    def test_prompt_injection_is_data_not_instruction(self):
        decision = authorize(attack_fixtures()[0])
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "untrusted_instruction")

    def test_unconsented_memory_is_blocked(self):
        decision = authorize(attack_fixtures()[1])
        self.assertEqual(decision.reason, "memory_ineligible")

    def test_polluted_tool_result_is_blocked(self):
        decision = authorize(attack_fixtures()[2])
        self.assertEqual(decision.reason, "tool_result_untrusted")

    def test_cross_subject_resource_is_blocked_before_context(self):
        decision = authorize(attack_fixtures()[3])
        self.assertEqual(decision.reason, "subject_isolation")
        self.assertEqual(decision.safe_context, ())

    def test_high_risk_action_requires_approval(self):
        decision = authorize(attack_fixtures()[4])
        self.assertEqual(decision.reason, "approval_required")

    def test_approved_same_subject_action_is_allowed(self):
        event = Event(
            "approved",
            "operator-a",
            "operator-a",
            "system",
            "publish_release",
            approved=True,
        )
        self.assertTrue(authorize(event).allowed)

    def test_all_attack_fixtures_are_blocked(self):
        report = run_suite(attack_fixtures())
        self.assertEqual(report["blocked"], 5)
        self.assertEqual(report["unexpected_allows"], 0)

    def test_release_requires_backup_and_rollback_target(self):
        report = run_suite(attack_fixtures())
        gate = release_gate(
            report,
            tests_passed=True,
            backup_verified=False,
            previous_version=None,
        )
        self.assertFalse(gate["allowed"])
        self.assertEqual(gate["reasons"], ("backup_unverified", "rollback_target_missing"))


if __name__ == "__main__":
    unittest.main()
