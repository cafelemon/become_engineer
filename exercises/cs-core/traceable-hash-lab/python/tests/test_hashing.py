import unittest

from traceable_hash_lab import (
    BucketEvent,
    DuplicateTrace,
    FrequencyRow,
    TraceableHashMap,
    bucket_index,
    build_bucket_chains,
    count_frequencies,
    deduplicate_preserving_order,
    first_collision,
    first_duplicate,
    trace_bucket_inserts,
)


class BucketTests(unittest.TestCase):
    def test_bucket_index_and_invalid_input(self) -> None:
        self.assertEqual(bucket_index(9, 4), 1)
        for count in (0, -1):
            with self.assertRaises(ValueError):
                bucket_index(1, count)
        with self.assertRaises(ValueError):
            bucket_index(-1, 4)

    def test_collision_trace_and_chains(self) -> None:
        keys = [1, 5, 9, 2]
        self.assertEqual(
            trace_bucket_inserts(keys, 4),
            [
                BucketEvent(1, 1, 0, False),
                BucketEvent(5, 1, 1, True),
                BucketEvent(9, 1, 2, True),
                BucketEvent(2, 2, 0, False),
            ],
        )
        self.assertEqual(build_bucket_chains(keys, 4), [[], [1, 5, 9], [2], []])
        self.assertEqual(first_collision(keys, 4), BucketEvent(5, 1, 1, True))
        self.assertIsNone(first_collision([], 4))


class HashMapTests(unittest.TestCase):
    def test_insert_update_lookup_and_sorted_items(self) -> None:
        table = TraceableHashMap()
        self.assertEqual(table.put(1, 10).comparisons, 0)
        self.assertEqual(table.put(5, 50).comparisons, 1)
        update = table.put(5, 55)
        self.assertFalse(update.inserted)
        self.assertEqual(update.comparisons, 2)
        self.assertEqual(table.size(), 2)
        self.assertEqual(table.get(5).value, 55)
        self.assertEqual(table.get(9).comparisons, 2)
        self.assertEqual(table.items_sorted(), [(1, 10), (5, 55)])

    def test_rehash_moves_old_entries_and_keeps_all_values(self) -> None:
        table = TraceableHashMap()
        for key in [1, 5, 9, 2]:
            table.put(key, key * 10)
        trace = table.put(13, 130)
        self.assertEqual((trace.bucket, trace.comparisons), (5, 1))
        self.assertEqual((trace.rehashed_from, trace.moved), (4, 4))
        self.assertEqual((table.bucket_count(), table.size()), (8, 5))
        self.assertEqual([table.get(key).value for key in [1, 5, 9, 2, 13]], [10, 50, 90, 20, 130])

    def test_load_boundary_does_not_rehash_and_erase_is_stable(self) -> None:
        table = TraceableHashMap(2)
        self.assertIsNone(table.put(0, 0).rehashed_from)
        self.assertIsNone(table.put(2, 20).rehashed_from)
        state = table.items_sorted()
        missing = table.erase(4)
        self.assertFalse(missing.removed)
        self.assertEqual(missing.comparisons, 2)
        self.assertEqual(table.items_sorted(), state)
        removed = table.erase(2)
        self.assertTrue(removed.removed)
        self.assertEqual(removed.comparisons, 2)
        self.assertEqual(table.items_sorted(), [(0, 0)])


class ApplicationTests(unittest.TestCase):
    def test_duplicate_boundaries(self) -> None:
        self.assertEqual(first_duplicate([]), DuplicateTrace(None, 0))
        self.assertEqual(first_duplicate([1, 2, 3]), DuplicateTrace(None, 3))
        self.assertEqual(first_duplicate([1, 1, 2]), DuplicateTrace(1, 2))
        self.assertEqual(first_duplicate([1, 2, 3, 1]), DuplicateTrace(1, 4))

    def test_frequency_sort_and_order_preserving_deduplication(self) -> None:
        values = [7, -1, 7, 3, -1]
        original = values.copy()
        self.assertEqual(count_frequencies(values), [FrequencyRow(-1, 2), FrequencyRow(3, 1), FrequencyRow(7, 2)])
        self.assertEqual(deduplicate_preserving_order(values), [7, -1, 3])
        self.assertEqual(values, original)


if __name__ == "__main__":
    unittest.main()
