from __future__ import annotations

import unittest

from concurrency_lab import locked_counter, lost_update_demo


class ConcurrencyLabTests(unittest.TestCase):
    def test_forced_interleaving_loses_one_update(self) -> None:
        self.assertEqual(lost_update_demo().actual, 1)

    def test_lock_protects_the_read_modify_write_region(self) -> None:
        result = locked_counter(workers=4, increments=500)
        self.assertEqual(result.actual, result.expected)
        self.assertEqual(result.actual, 2_000)

    def test_zero_workers_is_a_valid_empty_run(self) -> None:
        result = locked_counter(workers=0, increments=500)
        self.assertEqual(result.expected, 0)
        self.assertEqual(result.actual, 0)


if __name__ == "__main__":
    unittest.main()
