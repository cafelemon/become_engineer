from __future__ import annotations

import unittest

from traceable_array_lab import (
    CapacityEvent,
    GridCell,
    GrowthRow,
    GrowthSummary,
    RowTrace,
    SearchTrace,
    Utf8Trace,
    analyze_utf8,
    build_growth_rows,
    checked_at,
    checked_grid_at,
    count_adjacent_increases,
    linear_search,
    replace_at_copy,
    simulate_growth,
    sum_grid_row,
    summarize_growth,
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

    def test_utf8_trace_counts_ascii_chinese_and_four_byte_code_point(self) -> None:
        self.assertEqual(
            analyze_utf8("A工🧪".encode("utf-8")),
            Utf8Trace(8, 3, 1, 2),
        )
        self.assertEqual(analyze_utf8(b""), Utf8Trace(0, 0, 0, 0))

    def test_utf8_trace_rejects_all_malformed_families(self) -> None:
        invalid_inputs = (
            b"\x80",
            b"\xc2A",
            b"\xc0\xaf",
            b"\xed\xa0\x80",
            b"\xf4\x90\x80\x80",
            b"\xe5\xb7",
        )
        for data in invalid_inputs:
            with self.subTest(data=data):
                with self.assertRaises(UnicodeDecodeError):
                    analyze_utf8(data)

    def test_grid_access_uses_row_major_mapping(self) -> None:
        values = [1, 2, 3, 4, 5, 6]
        self.assertEqual(checked_grid_at(values, 2, 3, 0, 0), GridCell(1, 0))
        self.assertEqual(checked_grid_at(values, 2, 3, 1, 2), GridCell(6, 5))
        self.assertEqual(sum_grid_row(values, 2, 3, 0), RowTrace(6, 3))

    def test_grid_rejects_shape_and_coordinate_failures(self) -> None:
        with self.assertRaises(ValueError):
            checked_grid_at([1], 1, 2, 0, 0)
        with self.assertRaises(ValueError):
            checked_grid_at([], -1, 0, 0, 0)
        for row, column in ((-1, 0), (0, -1), (2, 0), (0, 3)):
            with self.subTest(row=row, column=column):
                with self.assertRaises(IndexError):
                    checked_grid_at([1, 2, 3, 4, 5, 6], 2, 3, row, column)
        with self.assertRaises(IndexError):
            sum_grid_row([], 0, 0, 0)

    def test_repeated_python_rows_are_aliases(self) -> None:
        grid = [[0] * 2] * 3
        grid[0][0] = 5
        self.assertEqual(grid, [[5, 0], [5, 0], [5, 0]])

    def test_growth_simulation_has_deterministic_events(self) -> None:
        events = simulate_growth([7, 3, 9, 3, 5])
        self.assertEqual(
            events,
            [
                CapacityEvent(7, 1, 1, 0, 1),
                CapacityEvent(3, 2, 2, 1, 2),
                CapacityEvent(9, 3, 4, 2, 3),
                CapacityEvent(3, 4, 4, 0, 1),
                CapacityEvent(5, 5, 8, 4, 5),
            ],
        )
        self.assertEqual(summarize_growth(events), GrowthSummary(5, 7, 12, 8))

    def test_growth_simulation_reserve_and_empty_boundaries(self) -> None:
        reserved = simulate_growth([7, 3, 9, 3, 5], initial_capacity=5)
        self.assertTrue(all(event.copies == 0 for event in reserved))
        self.assertEqual(summarize_growth([]), GrowthSummary(0, 0, 0, 0))
        with self.assertRaises(ValueError):
            simulate_growth([1], initial_capacity=-1)


if __name__ == "__main__":
    unittest.main()
