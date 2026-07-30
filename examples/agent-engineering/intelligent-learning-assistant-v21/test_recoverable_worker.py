from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from recoverable_worker import RecoverableWorker, VirtualClock, WorkerError, fixed_report


class RecoverableWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.clock = VirtualClock()
        self.worker = RecoverableWorker(Path(self.temp.name) / "worker.sqlite3", self.clock)
        self.worker.create_run("run", ["prepare", "write"])

    def tearDown(self) -> None:
        self.worker.close()
        self.temp.cleanup()

    def acquire(self, owner="worker-a", ttl=10):
        return self.worker.acquire("run", owner, ttl)

    def execute(self, step, key, payload=None, owner="worker-a", inject_failure=False):
        return self.worker.execute(
            run_id="run",
            owner_id=owner,
            step_id=step,
            idempotency_key=key,
            payload=payload or {"step": step},
            inject_failure=inject_failure,
        )

    def test_live_lease_excludes_other_worker(self):
        self.acquire()
        with self.assertRaisesRegex(WorkerError, "lease_busy"):
            self.acquire("worker-b")

    def test_expired_lease_can_be_taken_over(self):
        self.acquire()
        self.clock.advance(11)
        self.assertEqual(self.acquire("worker-b"), "worker-b:2")

    def test_stale_owner_cannot_execute(self):
        self.acquire()
        self.clock.advance(11)
        self.acquire("worker-b")
        with self.assertRaisesRegex(WorkerError, "lease_lost"):
            self.execute("prepare", "k1", owner="worker-a")

    def test_steps_must_follow_plan_order(self):
        self.acquire()
        with self.assertRaisesRegex(WorkerError, "step_out_of_order"):
            self.execute("write", "k2")

    def test_injected_crash_rolls_back_effect_and_step(self):
        self.acquire()
        with self.assertRaisesRegex(WorkerError, "injected_failure"):
            self.execute("prepare", "k1", inject_failure=True)
        self.assertEqual(self.worker.effect_count(), 0)
        self.assertEqual(self.worker.next_step("run"), "prepare")

    def test_same_step_retry_is_replayed_without_duplicate(self):
        self.acquire()
        self.assertFalse(self.execute("prepare", "k1"))
        self.assertTrue(self.execute("prepare", "k1"))
        self.assertEqual(self.worker.effect_count(), 1)

    def test_changed_retry_is_rejected(self):
        self.acquire()
        self.execute("prepare", "k1")
        with self.assertRaisesRegex(WorkerError, "step_conflict"):
            self.execute("prepare", "k1", payload={"changed": True})

    def test_resume_starts_at_first_uncommitted_step_and_report_is_fixed(self):
        self.acquire()
        self.execute("prepare", "k1")
        self.assertEqual(self.worker.next_step("run"), "write")
        report = fixed_report()
        self.assertIn("takeover-after-expiry:true", report)
        self.assertIn("replay:true", report)
        self.assertIn("side-effects:2", report)


if __name__ == "__main__":
    unittest.main()
