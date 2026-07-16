import unittest

from traceable_search_sort_lab import (
    TaggedValue,
    bottom_up_merge_sort,
    insertion_sort,
    merge_sorted,
    preserves_equal_order,
    selection_sort,
)


class SortingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.values = [
            TaggedValue(3, "A"),
            TaggedValue(1, "B"),
            TaggedValue(3, "C"),
            TaggedValue(2, "D"),
        ]

    def test_insertion_sort_is_stable_and_counts_operations(self) -> None:
        trace = insertion_sort(self.values)
        self.assertEqual([item.tag for item in trace.items], ["B", "D", "A", "C"])
        self.assertEqual((trace.comparisons, trace.shifts), (5, 3))
        self.assertTrue(preserves_equal_order(self.values, trace.items))

    def test_selection_sort_reproduces_instability(self) -> None:
        trace = selection_sort(self.values)
        self.assertEqual([item.tag for item in trace.items], ["B", "D", "C", "A"])
        self.assertEqual((trace.comparisons, trace.swaps), (6, 2))
        self.assertFalse(preserves_equal_order(self.values, trace.items))

    def test_sorting_returns_copy_and_supports_stable_descending(self) -> None:
        original = list(self.values)
        trace = insertion_sort(self.values, descending=True)
        self.assertEqual(self.values, original)
        self.assertEqual([item.tag for item in trace.items], ["A", "C", "D", "B"])
        self.assertTrue(preserves_equal_order(self.values, trace.items))

    def test_empty_single_sorted_reverse_and_negative_values(self) -> None:
        self.assertEqual(insertion_sort([]).items, ())
        one = [TaggedValue(-1, "A")]
        self.assertEqual(selection_sort(one).items, tuple(one))
        sorted_values = [TaggedValue(-2, "A"), TaggedValue(0, "B")]
        self.assertEqual(insertion_sort(sorted_values).shifts, 0)
        self.assertEqual(insertion_sort(list(reversed(sorted_values))).shifts, 1)

    def test_merge_accepts_empty_side_and_prefers_left_on_ties(self) -> None:
        left = [TaggedValue(3, "L")]
        right = [TaggedValue(3, "R")]
        self.assertEqual(merge_sorted([], right).items, tuple(right))
        self.assertEqual(merge_sorted(left, []).items, tuple(left))
        merged = merge_sorted(left, right)
        self.assertEqual([item.tag for item in merged.items], ["L", "R"])
        self.assertEqual((merged.comparisons, merged.writes), (1, 2))

    def test_bottom_up_merge_records_passes_and_counts(self) -> None:
        trace = bottom_up_merge_sort(self.values)
        self.assertEqual([item.tag for item in trace.items], ["B", "D", "A", "C"])
        self.assertEqual([merge_pass.width for merge_pass in trace.passes], [1, 2])
        self.assertEqual((trace.comparisons, trace.writes), (5, 8))
        self.assertTrue(preserves_equal_order(self.values, trace.items))

    def test_merge_handles_odd_length_and_stable_descending(self) -> None:
        values = [TaggedValue(2, "A"), TaggedValue(1, "B"), TaggedValue(2, "C")]
        trace = bottom_up_merge_sort(values, descending=True)
        self.assertEqual([item.tag for item in trace.items], ["A", "C", "B"])
        self.assertTrue(preserves_equal_order(values, trace.items))
        self.assertEqual(values[0].tag, "A")


if __name__ == "__main__":
    unittest.main()
