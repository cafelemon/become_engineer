from __future__ import annotations

import unittest

from traceable_graph_traversal_lab import (
    Edge,
    UndirectedGraph,
    build_adjacency_matrix,
    degree_sequence,
    describe_graph,
    has_edge,
)


class GraphTests(unittest.TestCase):
    def test_empty_graph(self) -> None:
        graph = UndirectedGraph(0, ())
        self.assertEqual(describe_graph(graph).adjacency_entries, 0)
        self.assertEqual(build_adjacency_matrix(graph), ())

    def test_edges_are_canonical_and_neighbors_sorted(self) -> None:
        source = [(2, 0), (2, 1)]
        graph = UndirectedGraph(3, source)
        source.append((0, 1))
        self.assertEqual(graph.edges, (Edge(0, 2), Edge(1, 2)))
        self.assertEqual(graph.neighbors(2), (0, 1))
        self.assertEqual(degree_sequence(graph), (1, 1, 2))

    def test_matrix_is_symmetric_and_has_edge_checks_vertices(self) -> None:
        graph = UndirectedGraph(3, ((0, 2),))
        self.assertEqual(
            build_adjacency_matrix(graph),
            ((False, False, True), (False, False, False), (True, False, False)),
        )
        self.assertTrue(has_edge(graph, 2, 0))
        self.assertFalse(has_edge(graph, 0, 1))
        with self.assertRaises(IndexError):
            has_edge(graph, -1, 0)

    def test_invalid_graphs_fail_without_partial_result(self) -> None:
        invalid_cases = (
            (-1, ()),
            (2, ((0, 2),)),
            (2, ((-1, 0),)),
            (2, ((1, 1),)),
            (3, ((0, 2), (2, 0))),
        )
        for vertex_count, edges in invalid_cases:
            with self.subTest(vertex_count=vertex_count, edges=edges):
                with self.assertRaises(ValueError):
                    UndirectedGraph(vertex_count, edges)


if __name__ == "__main__":
    unittest.main()
