from __future__ import annotations

import unittest

from traceable_graph_traversal_lab import (
    Edge,
    UndirectedGraph,
    build_component_labels,
    depth_first_components,
)


class DfsTests(unittest.TestCase):
    def test_components_cycle_and_exact_counts(self) -> None:
        graph = UndirectedGraph(7, ((0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (5, 6)))
        trace = depth_first_components(graph)
        self.assertEqual(trace.components, ((0, 1, 3, 2, 4), (5, 6)))
        self.assertEqual((trace.visits, trace.edge_checks, trace.max_depth), (7, 12, 3))
        self.assertEqual(trace.cycle_edge, Edge(0, 2))
        self.assertEqual(build_component_labels(graph).labels, (0, 0, 0, 0, 0, 1, 1))

    def test_parent_edge_is_not_a_cycle(self) -> None:
        graph = UndirectedGraph(3, ((0, 1), (1, 2)))
        trace = depth_first_components(graph)
        self.assertIsNone(trace.cycle_edge)
        self.assertEqual(trace.components, ((0, 1, 2),))

    def test_empty_and_isolated_vertices(self) -> None:
        empty = depth_first_components(UndirectedGraph(0, ()))
        self.assertEqual((empty.components, empty.max_depth), ((), -1))
        isolated = depth_first_components(UndirectedGraph(3, ()))
        self.assertEqual(isolated.components, ((0,), (1,), (2,)))
        self.assertEqual(isolated.edge_checks, 0)
        labels = build_component_labels(UndirectedGraph(3, ()))
        self.assertEqual((labels.labels, labels.component_count), ((0, 1, 2), 3))


if __name__ == "__main__":
    unittest.main()
