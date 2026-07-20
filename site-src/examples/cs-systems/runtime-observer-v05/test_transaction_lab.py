from __future__ import annotations

import tempfile
import unittest

from transaction_lab import (
    fresh_database,
    lock_wait_then_retry,
    reject_overdraft,
    rollback_transfer,
    snapshot_read,
)


class TransactionLabTests(unittest.TestCase):
    def test_failure_rolls_back_both_sides_of_transfer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rollback_transfer(fresh_database(directory, "rollback.sqlite3"))
        self.assertEqual(result.before, (100, 100))
        self.assertEqual(result.after, result.before)

    def test_constraint_rejects_negative_balance_and_preserves_total(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = reject_overdraft(fresh_database(directory, "constraint.sqlite3"))
        self.assertTrue(result.rejected)
        self.assertEqual(result.balances, (100, 100))
        self.assertEqual(sum(result.balances), 200)

    def test_second_writer_is_blocked_then_retry_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = lock_wait_then_retry(fresh_database(directory, "lock.sqlite3"))
        self.assertTrue(result.blocked)
        self.assertTrue(result.retry_succeeded)

    def test_wal_reader_keeps_snapshot_until_transaction_ends(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = snapshot_read(fresh_database(directory, "snapshot.sqlite3"))
        self.assertEqual(result.before, 100)
        self.assertEqual(result.during, 100)
        self.assertEqual(result.after, 120)


if __name__ == "__main__":
    unittest.main()
