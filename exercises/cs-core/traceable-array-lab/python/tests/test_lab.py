from __future__ import annotations

import unittest

from traceable_array_lab import (
    GrowthRow,
    SearchTrace,
    build_growth_rows,
    checked_at,
    count_adjacent_increases,
    linear_search,
    replace_at_copy,
)


class ArrayLabTests(unittest.TestCase):
    def test_checked_at_accepts_first_and_last_positions(self) -> None:
        values = [7, 3, 9]
        self.assertEqual(checked_at(values, 0), 7)
        self.assertEqual(checked_at(values, 2), 9)

    def test_checked_at_rejects_negative_empty_and_size_index(self) -> None:
        for values, index in (([1], -1), ([1], 1), ([], 0)):
            with self.subTest(values=values, index=index):
                with self.assertRaises(IndexError):
                    checked_at(values, index)

    def test_replace_at_copy_keeps_input_unchanged(self) -> None:
        original = [7, 3, 9]
        changed = replace_at_copy(original, 1, 8)
        self.assertEqual(changed, [7, 8, 9])
        self.assertEqual(original, [7, 3, 9])

    def test_replace_at_copy_uses_same_boundary_contract(self) -> None:
        with self.assertRaises(IndexError):
            replace_at_copy([1], -1, 2)
        with self.assertRaises(IndexError):
            replace_at_copy([1], 1, 2)

    def test_linear_search_returns_first_match_and_count(self) -> None:
        self.assertEqual(linear_search([7, 3, 9, 3], 3), SearchTrace(1, 2))

    def test_linear_search_missing_and_empty_use_exact_counts(self) -> None:
        self.assertEqual(linear_search([7, 3, 9], 4), SearchTrace(None, 3))
        self.assertEqual(linear_search([], 4), SearchTrace(None, 0))

    def test_growth_rows_use_deterministic_formulas(self) -> None:
        self.assertEqual(
            build_growth_rows([4, 8]),
            [GrowthRow(4, 1, 4, 6), GrowthRow(8, 1, 8, 28)],
        )

    def test_growth_rows_handle_zero_and_reject_negative(self) -> None:
        self.assertEqual(build_growth_rows([0]), [GrowthRow(0, 0, 0, 0)])
        with self.assertRaises(ValueError):
            build_growth_rows([-1])

    def test_adjacent_increases_compare_at_most_n_minus_one(self) -> None:
        self.assertEqual(count_adjacent_increases([]).comparisons, 0)
        self.assertEqual(count_adjacent_increases([4]).comparisons, 0)
        self.assertEqual(count_adjacent_increases([1, 2, 3]).comparisons, 2)
        self.assertEqual(count_adjacent_increases([1, 1, 2]).increases, 1)


if __name__ == "__main__":
    unittest.main()
