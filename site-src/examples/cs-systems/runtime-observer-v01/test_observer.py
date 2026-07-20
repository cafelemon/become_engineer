from __future__ import annotations

import unittest

from observer import run_worker


class RuntimeObserverTests(unittest.TestCase):
    def test_success_reports_a_distinct_child_and_zero_exit(self) -> None:
        result = run_worker("success")
        self.assertFalse(result.timed_out)
        self.assertEqual(result.returncode, 0)
        self.assertNotEqual(result.child_pid, result.parent_pid)
        self.assertEqual(result.reported_parent_pid, result.parent_pid)
        self.assertEqual(result.stderr, "")

    def test_failure_keeps_stderr_and_nonzero_exit(self) -> None:
        result = run_worker("fail")
        self.assertFalse(result.timed_out)
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.stderr, "simulated worker failure")

    def test_timeout_is_not_reported_as_a_normal_exit(self) -> None:
        result = run_worker("sleep", timeout=0.05)
        self.assertTrue(result.timed_out)
        self.assertIsNone(result.returncode)


if __name__ == "__main__":
    unittest.main()
