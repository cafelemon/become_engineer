import unittest

from traceable_search_sort_lab import (
    SortedValues,
    equal_range,
    linear_search,
    lower_bound,
    upper_bound,
)


class SearchingTests(unittest.TestCase):
    def test_constructor_copies_and_rejects_unsorted_input(self) -> None:
        source = [1, 3, 3]
        values = SortedValues.from_values(source)
        source[0] = 9
        self.assertEqual(values.values, (1, 3, 3))
        with self.assertRaises(ValueError):
            SortedValues.from_values([1, 4, 2])
        with self.assertRaises(ValueError):
            SortedValues([3, 1])

    def test_empty_search_and_bounds(self) -> None:
        values = SortedValues.from_values([])
        self.assertEqual(linear_search(values, 3).comparisons, 0)
        self.assertIsNone(linear_search(values, 3).index)
        self.assertEqual(lower_bound(values, 3).index, 0)
        self.assertEqual(upper_bound(values, 3).index, 0)

    def test_linear_search_reports_first_match_and_exact_count(self) -> None:
        values = SortedValues.from_values([1, 3, 3, 7])
        self.assertEqual(linear_search(values, 3).index, 1)
        self.assertEqual(linear_search(values, 3).comparisons, 2)
        self.assertEqual(linear_search(values, 9).comparisons, 4)

    def test_bounds_cover_duplicates_and_return_length(self) -> None:
        values = SortedValues.from_values([1, 3, 3, 3, 7, 9])
        self.assertEqual(lower_bound(values, 3).index, 1)
        self.assertEqual(upper_bound(values, 3).index, 4)
        self.assertEqual(lower_bound(values, 10).index, 6)
        self.assertEqual(upper_bound(values, 9).index, 6)

    def test_fixed_bound_comparison_counts(self) -> None:
        values = SortedValues.from_values([1, 3, 3, 3, 7, 9])
        self.assertEqual(lower_bound(values, 3).comparisons, 3)
        self.assertEqual(upper_bound(values, 3).comparisons, 3)
        self.assertEqual(equal_range(values, 3).comparisons, 6)

    def test_equal_range_for_present_and_missing_target(self) -> None:
        values = SortedValues.from_values([1, 3, 3, 7])
        present = equal_range(values, 3)
        missing = equal_range(values, 5)
        self.assertEqual((present.first, present.last), (1, 3))
        self.assertEqual((missing.first, missing.last), (3, 3))


if __name__ == "__main__":
    unittest.main()
