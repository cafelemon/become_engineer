import unittest

from controlled_write import (
    ConfirmationAuthority,
    ControlledWriteError,
    ControlledWriteExecutor,
    LearningPlanStore,
    Principal,
    WriteCall,
    demo_call,
    fixed_report,
)


class ControlledWriteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.principal = Principal(
            "learner-001", frozenset({"learning_plan:write"})
        )
        self.store = LearningPlanStore()
        self.authority = ConfirmationAuthority()
        self.executor = ControlledWriteExecutor(self.store, self.authority)

    def approve(self, call, *, now=100, ttl=60):
        return self.authority.issue(
            call, self.principal, now=now, human_approved=True, ttl_seconds=ttl
        )

    def test_permission_and_ownership_are_required_before_write(self) -> None:
        call = demo_call()
        for principal in [
            Principal("learner-001", frozenset()),
            Principal("learner-002", frozenset({"learning_plan:write"})),
        ]:
            result = self.executor.execute(
                call, principal, confirmation=None, now=100
            )
            self.assertEqual(result.error_code, "forbidden")
        self.assertEqual(self.store.write_count, 0)

    def test_missing_confirmation_is_default_denied(self) -> None:
        result = self.executor.execute(
            demo_call(), self.principal, confirmation=None, now=100
        )
        self.assertEqual(result.error_code, "confirmation_required")
        self.assertEqual(self.store.goals, {})

    def test_expired_or_mismatched_confirmation_is_rejected(self) -> None:
        call = demo_call()
        expired = self.approve(call, now=100, ttl=1)
        result = self.executor.execute(
            call, self.principal, confirmation=expired, now=102
        )
        self.assertEqual(result.error_code, "confirmation_expired")
        other = demo_call(weekly_minutes=240)
        grant = self.approve(call)
        result = self.executor.execute(
            other, self.principal, confirmation=grant, now=101
        )
        self.assertEqual(result.error_code, "confirmation_mismatch")
        self.assertEqual(self.store.write_count, 0)

    def test_confirmed_write_happens_once_and_consumes_grant(self) -> None:
        call = demo_call()
        grant = self.approve(call)
        result = self.executor.execute(
            call, self.principal, confirmation=grant, now=101
        )
        self.assertEqual((result.status, result.replayed), ("ok", False))
        self.assertEqual(self.store.goals["learner-001"], 180)
        second_call = demo_call(idempotency_key="idem_other01")
        reused = self.executor.execute(
            second_call, self.principal, confirmation=grant, now=102
        )
        self.assertEqual(reused.error_code, "invalid_confirmation")
        self.assertEqual(self.store.write_count, 1)

    def test_same_idempotency_key_and_payload_replays_without_second_write(self) -> None:
        call = demo_call()
        first = self.executor.execute(
            call, self.principal, confirmation=self.approve(call), now=101
        )
        retry = WriteCall("call_retry1", call.name, call.arguments)
        second = self.executor.execute(
            retry, self.principal, confirmation=None, now=102
        )
        self.assertFalse(first.replayed)
        self.assertTrue(second.replayed)
        self.assertEqual(self.store.write_count, 1)

    def test_same_idempotency_key_with_different_payload_conflicts(self) -> None:
        first = demo_call()
        self.executor.execute(
            first, self.principal, confirmation=self.approve(first), now=101
        )
        conflicting = demo_call(weekly_minutes=240)
        result = self.executor.execute(
            conflicting,
            self.principal,
            confirmation=self.approve(conflicting),
            now=102,
        )
        self.assertEqual(result.error_code, "idempotency_conflict")
        self.assertEqual(self.store.goals["learner-001"], 180)
        self.assertEqual(self.store.write_count, 1)

    def test_unknown_tool_and_invalid_values_default_deny(self) -> None:
        calls = [
            WriteCall("call_bad1", "delete_account", demo_call().arguments),
            demo_call(weekly_minutes=True),
            demo_call(weekly_minutes=601),
            demo_call(idempotency_key="../bad"),
        ]
        for call in calls:
            result = self.executor.execute(
                call, self.principal, confirmation=None, now=100
            )
            self.assertIn(result.error_code, {"unknown_tool", "invalid_arguments"})
        with self.assertRaises(ControlledWriteError):
            self.authority.issue(
                demo_call(), self.principal, now=100, human_approved=False
            )
        self.assertEqual(self.store.write_count, 0)

    def test_fixed_report_proves_confirmation_and_idempotency(self) -> None:
        report = fixed_report()
        self.assertIn("unconfirmed=status:error,error:confirmation_required,writes:0", report)
        self.assertIn("retry=status:ok,replayed:true,writes:1", report)
        self.assertIn("bound-arguments:true", report)
        self.assertIn("write-once,replay-safe", report)
        self.assertNotIn("idem_week001", report)
        self.assertNotIn("grant_", report)


if __name__ == "__main__":
    unittest.main()
