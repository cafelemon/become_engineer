import os
import unittest
from datetime import datetime, timedelta, timezone

from long_run_store import RunStore


URL = os.environ["AGENT_POSTGRES_URL"]
NOW = datetime.now(timezone.utc)


class LongRunStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = RunStore(URL); cls.store.migrate()

    @classmethod
    def tearDownClass(cls): cls.store.close()

    def setUp(self): self.store.reset()

    def run_with_lease(self):
        run = self.store.create_run("alice")
        self.assertTrue(self.store.acquire(run, "w1", NOW))
        return run

    def test_only_one_live_lease_owner(self):
        run = self.run_with_lease()
        self.assertFalse(self.store.acquire(run, "w2", NOW + timedelta(seconds=1)))

    def test_expired_lease_can_be_recovered(self):
        run = self.run_with_lease()
        self.assertTrue(self.store.acquire(run, "w2", NOW + timedelta(seconds=31)))

    def test_checkpoint_and_step_are_atomic(self):
        run = self.run_with_lease(); self.store.checkpoint(run, "w1", "retrieve", {"cursor": 1})
        self.assertEqual({"cursor": 1}, self.store.run(run)["checkpoint"])
        self.assertEqual(1, self.store.db.execute("SELECT count(*) FROM run_steps").fetchone()[0])

    def test_checkpoint_requires_current_lease(self):
        run = self.run_with_lease()
        with self.assertRaises(PermissionError): self.store.checkpoint(run, "w2", "x", {})

    def test_approve_resumes_run(self):
        run = self.run_with_lease(); approval = self.store.request_approval(run, {"action": "publish"})
        self.store.decide(approval, "alice", "approve")
        self.assertTrue(self.store.resume(run, "w2", NOW + timedelta(seconds=31)))

    def test_edit_replaces_only_proposed_payload(self):
        run = self.run_with_lease(); approval = self.store.request_approval(run, {"target": "wrong"})
        result = self.store.decide(approval, "alice", "edit", {"target": "right"})
        self.assertEqual({"target": "right"}, result["payload"])

    def test_reject_is_terminal_and_cross_subject_hidden(self):
        run = self.run_with_lease(); approval = self.store.request_approval(run, {"action": "delete"})
        with self.assertRaises(KeyError): self.store.decide(approval, "bob", "approve")
        self.assertEqual("rejected", self.store.decide(approval, "alice", "reject")["status"])
        self.assertFalse(self.store.resume(run, "w2", NOW + timedelta(seconds=31)))

    def test_effect_is_idempotent_by_key(self):
        run = self.run_with_lease()
        first = self.store.perform_effect(run, "send:1", {"sent": True})
        second = self.store.perform_effect(run, "send:1", {"sent": False})
        self.assertEqual(first, second)
        self.assertEqual(1, self.store.db.execute("SELECT count(*) FROM effect_receipts").fetchone()[0])


if __name__ == "__main__": unittest.main()
