from __future__ import annotations

import unittest

from traceable_priority_shortest_path_lab import (
    StableMinPriorityQueue, TraceableMinHeap, WeightedGraph, build_dijkstra_report,
    build_heap_report, build_min_heap, build_queue_report, dijkstra, drain_by_priority,
    is_min_heap, sample_weighted_graph, shortest_path, vertices_within_distance,
)
from traceable_priority_shortest_path_lab.weighted import MAX_DISTANCE


class HeapTests(unittest.TestCase):
    def test_fixed_trace_and_underflow(self) -> None:
        heap = TraceableMinHeap()
        events = [heap.push(value) for value in (7, 3, 9, 1, 5)]
        self.assertEqual(heap.values, (1, 3, 9, 7, 5))
        self.assertEqual(sum(event.comparisons for event in events), 5)
        self.assertEqual(sum(event.swaps for event in events), 3)
        popped = heap.pop_min()
        self.assertEqual((popped.value, popped.values, popped.comparisons, popped.swaps), (1, (3, 5, 9, 7), 3, 1))
        while not heap.empty:
            heap.pop_min()
        with self.assertRaises(IndexError):
            heap.peek_min()
        self.assertEqual(heap.values, ())

    def test_build_and_invariant(self) -> None:
        original = [9, -1, 7, -1, 3, 2]
        trace = build_min_heap(original)
        self.assertTrue(is_min_heap(trace.values))
        self.assertFalse(is_min_heap((2, 1, 3)))
        self.assertEqual(original, [9, -1, 7, -1, 3, 2])


class QueueTests(unittest.TestCase):
    def test_stable_order_and_input_unchanged(self) -> None:
        tasks = [("same", 1), ("same", 1), ("urgent", -1), ("later", 2)]
        result = drain_by_priority(tasks)
        self.assertEqual([(item.label, item.priority, item.sequence) for item in result], [
            ("urgent", -1, 2), ("same", 1, 0), ("same", 1, 1), ("later", 2, 3),
        ])
        self.assertEqual(tasks[0], ("same", 1))

    def test_underflow_is_unchanged(self) -> None:
        queue = StableMinPriorityQueue()
        with self.assertRaises(IndexError):
            queue.pop()
        self.assertTrue(queue.empty)


class DijkstraTests(unittest.TestCase):
    def test_fixed_trace_and_path(self) -> None:
        graph = sample_weighted_graph()
        trace = dijkstra(graph, 0)
        self.assertEqual(trace.settled, (0, 2, 1, 3, 4, 5))
        self.assertEqual(trace.distances, (0, 3, 1, 4, 7, 8, None))
        self.assertEqual(trace.parents, (None, 2, 0, 1, 3, 4, None))
        self.assertEqual((trace.edge_checks, trace.relaxations, trace.queue_pushes, trace.stale_pops, trace.max_frontier), (16, 8, 9, 3, 4))
        self.assertEqual(shortest_path(graph, 0, 5).path, (0, 2, 1, 3, 4, 5))
        self.assertEqual(shortest_path(graph, 0, 6).path, ())
        self.assertEqual(vertices_within_distance(graph, 0, 4), (0, 2, 1, 3))

    def test_validation_and_overflow(self) -> None:
        invalid = [((0, 0, 1),), ((0, 2, 1),), ((0, 1, -1),)]
        for edges in invalid:
            with self.assertRaises(ValueError):
                WeightedGraph(2, edges)
        with self.assertRaises(ValueError):
            WeightedGraph(2, ((0, 1, 1), (1, 0, 2)))
        graph = WeightedGraph(3, ((0, 1, MAX_DISTANCE), (1, 2, 1)))
        with self.assertRaises(OverflowError):
            dijkstra(graph, 0)

    def test_zero_weight_and_equal_distance(self) -> None:
        graph = WeightedGraph(4, ((0, 1, 0), (0, 2, 1), (1, 2, 1)))
        trace = dijkstra(graph, 0)
        self.assertEqual(trace.distances, (0, 0, 1, None))
        self.assertEqual(trace.parents[2], 0)


class ReportingTests(unittest.TestCase):
    def test_reports(self) -> None:
        self.assertIn("comparisons=5，swaps=3", build_heap_report())
        self.assertIn("equal_priority_fifo=yes", build_queue_report())
        self.assertIn("stale_pops=3，max_frontier=4", build_dijkstra_report())


if __name__ == "__main__":
    unittest.main()
