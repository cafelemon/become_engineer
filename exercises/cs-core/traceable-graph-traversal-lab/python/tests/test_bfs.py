from __future__ import annotations

import unittest

from traceable_graph_traversal_lab import UndirectedGraph, breadth_first, reachable_within, shortest_path


class BfsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = UndirectedGraph(7, ((0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (5, 6)))

    def test_distances_parents_and_exact_counts(self) -> None:
        trace = breadth_first(self.graph, 0)
        self.assertEqual(trace.order, (0, 1, 2, 3, 4))
        self.assertEqual(trace.distances, (0, 1, 1, 2, 3, None, None))
        self.assertEqual(trace.parents, (None, 0, 0, 1, 3, None, None))
        self.assertEqual((trace.visits, trace.edge_checks, trace.max_frontier), (5, 10, 2))

    def test_shortest_path_and_unreachable_target(self) -> None:
        self.assertEqual(shortest_path(self.graph, 0, 4).path, (0, 1, 3, 4))
        self.assertEqual(shortest_path(self.graph, 0, 4).distance, 3)
        self.assertEqual(shortest_path(self.graph, 0, 6).path, ())
        self.assertIsNone(shortest_path(self.graph, 0, 6).distance)

    def test_single_vertex_and_invalid_vertices(self) -> None:
        trace = breadth_first(UndirectedGraph(1, ()), 0)
        self.assertEqual((trace.order, trace.max_frontier), ((0,), 1))
        with self.assertRaises(IndexError):
            breadth_first(self.graph, -1)
        with self.assertRaises(IndexError):
            shortest_path(self.graph, 0, 7)

    def test_reachable_within_preserves_bfs_order(self) -> None:
        self.assertEqual(reachable_within(self.graph, 0, 2), (0, 1, 2, 3))
        with self.assertRaises(ValueError):
            reachable_within(self.graph, 0, -1)


if __name__ == "__main__":
    unittest.main()
