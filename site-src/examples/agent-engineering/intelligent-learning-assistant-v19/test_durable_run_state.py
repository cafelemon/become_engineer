from pathlib import Path
import tempfile
import unittest

from durable_run_state import RunRepository, RunStateError, fixed_report


class DurableRunStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = RunRepository(Path(self.temporary.name) / "runs.db")
        self.repository.create_run("run_test01", "learner-001", now=100)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def transition(self, **overrides):
        values = {
            "run_id": "run_test01",
            "expected_version": 0,
            "event_id": "evt_start1",
            "event_type": "run_started",
            "next_status": "running",
            "checkpoint": {"next_step": "read_status"},
            "now": 101,
        }
        values.update(overrides)
        return self.repository.transition(**values)

    def test_create_and_read_initial_snapshot(self) -> None:
        snapshot = self.repository.get_run("run_test01")
        self.assertEqual(
            (snapshot.status, snapshot.version, dict(snapshot.checkpoint)),
            ("created", 0, {}),
        )
        with self.assertRaisesRegex(RunStateError, "already"):
            self.repository.create_run("run_test01", "learner-001", now=101)

    def test_transition_commits_event_and_snapshot_atomically(self) -> None:
        snapshot = self.transition()
        events = self.repository.events("run_test01")
        self.assertEqual((snapshot.status, snapshot.version), ("running", 1))
        self.assertEqual(len(events), 1)
        self.assertEqual(
            (events[0].sequence, events[0].event_type), (1, "run_started")
        )

    def test_invalid_status_transition_is_rejected(self) -> None:
        with self.assertRaisesRegex(RunStateError, "transition"):
            self.transition(
                event_id="evt_bad001",
                event_type="run_completed",
                next_status="completed",
            )
        self.assertEqual(self.repository.get_run("run_test01").version, 0)
        self.assertEqual(self.repository.events("run_test01"), ())

    def test_stale_expected_version_is_rejected(self) -> None:
        self.transition()
        with self.assertRaisesRegex(RunStateError, "version"):
            self.transition(
                event_id="evt_stale1",
                event_type="run_failed",
                next_status="failed",
            )
        self.assertEqual(self.repository.get_run("run_test01").version, 1)

    def test_duplicate_event_replays_and_changed_payload_conflicts(self) -> None:
        first = self.transition()
        replay = self.transition(now=999)
        self.assertFalse(first.replayed)
        self.assertTrue(replay.replayed)
        self.assertEqual(len(self.repository.events("run_test01")), 1)
        with self.assertRaisesRegex(RunStateError, "another transition"):
            self.transition(
                next_status="waiting_input",
                event_type="input_requested",
            )

    def test_injected_failure_rolls_back_event_and_snapshot(self) -> None:
        with self.assertRaisesRegex(RunStateError, "rolled back"):
            self.transition(fail_after_event=True)
        snapshot = self.repository.get_run("run_test01")
        self.assertEqual((snapshot.status, snapshot.version), ("created", 0))
        self.assertEqual(self.repository.events("run_test01"), ())

    def test_checkpoint_rejects_reasoning_and_unbounded_values(self) -> None:
        for checkpoint in [
            {"reasoning": "hidden"},
            {"prompt": "private"},
            {"completed_step_ids": [f"step-{index}" for index in range(9)]},
            {"last_tool_status": "maybe"},
        ]:
            with self.subTest(checkpoint=checkpoint):
                with self.assertRaises(RunStateError):
                    self.transition(checkpoint=checkpoint)
        self.assertEqual(self.repository.events("run_test01"), ())

    def test_fixed_report_proves_replay_stale_and_atomic_rollback(self) -> None:
        report = fixed_report()
        self.assertIn("replayed:true,events:2", report)
        self.assertIn("stale:stale_version,current-version:2", report)
        self.assertIn("injected-failure:storage_failure,status:waiting_input", report)
        self.assertIn("no-hidden-chain-of-thought", report)
        self.assertNotIn("learner-001", report)


if __name__ == "__main__":
    unittest.main()
