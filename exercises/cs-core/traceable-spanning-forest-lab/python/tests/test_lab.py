from __future__ import annotations

import subprocess
import sys
import unittest

from traceable_spanning_forest_lab import (
    DisjointSet,
    SpanningGraph,
    compare_spanning_forests,
    kruskal_forest,
    lazy_prim_forest,
    minimum_spanning_tree,
    rejected_cycle_edges,
)


class DisjointSetTests(unittest.TestCase):
    def test_zero_single_and_bounds(self) -> None:
        self.assertEqual(DisjointSet(0).groups(), ())
        dsu = DisjointSet(1)
        self.assertEqual(dsu.find(0).visits, 1)
        with self.assertRaises(IndexError):
            dsu.find(1)

    def test_union_tie_and_repeated_merge(self) -> None:
        dsu = DisjointSet(4)
        self.assertEqual(dsu.union(1, 0).root, 0)
        self.assertEqual(dsu.union(3, 2).root, 2)
        self.assertEqual(dsu.union(2, 0).root, 0)
        self.assertFalse(dsu.union(3, 1).merged)
        self.assertEqual(dsu.component_count, 1)

    def test_full_compression_and_groups(self) -> None:
        dsu = DisjointSet(7)
        for edge in ((0, 1), (2, 3), (0, 2), (4, 5), (5, 6), (3, 6)):
            dsu.union(*edge)
        self.assertEqual(dsu.parents, (0, 0, 0, 0, 0, 4, 4))
        trace = dsu.find(5)
        self.assertEqual((trace.path, trace.visits, trace.compressions), ((5, 4, 0), 3, 1))
        self.assertEqual(dsu.groups()[0].members, tuple(range(7)))


class ForestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = SpanningGraph(7, (
            (0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5),
            (2, 3, 3), (2, 4, 6), (3, 4, 2), (5, 6, -1),
        ))

    def test_graph_validation(self) -> None:
        for edges in (((0, 0, 1),), ((0, 2, 1),), ((0, 1, 1), (1, 0, 2))):
            with self.assertRaises(ValueError):
                SpanningGraph(2, edges)
        self.assertEqual(SpanningGraph(2, ((0, 1, 0),)).edges[0].weight, 0)

    def test_kruskal_disconnected_and_cycles(self) -> None:
        forest = kruskal_forest(self.graph)
        self.assertEqual((forest.total_weight, forest.component_count, len(forest.edges)), (7, 2, 5))
        self.assertEqual(len(rejected_cycle_edges(self.graph)), 3)
        with self.assertRaises(ValueError):
            minimum_spanning_tree(self.graph)

    def test_input_order_and_equal_weights_are_deterministic(self) -> None:
        first = SpanningGraph(4, ((2, 3, 1), (0, 2, 1), (0, 1, 1), (1, 3, 1)))
        second = SpanningGraph(4, reversed(first.edges))
        self.assertEqual(kruskal_forest(first).edges, kruskal_forest(second).edges)

    def test_prim_counts_and_comparison(self) -> None:
        trace = lazy_prim_forest(self.graph)
        self.assertEqual(trace.component_starts, (0, 5))
        self.assertEqual((trace.edge_scans, trace.queue_pushes, trace.stale_pops, trace.max_frontier), (16, 8, 3, 4))
        self.assertTrue(compare_spanning_forests(self.graph).matching)

    def test_empty_graph_and_isolated_vertices(self) -> None:
        trace = lazy_prim_forest(SpanningGraph(3, ()))
        self.assertEqual((trace.component_starts, trace.forest.component_count), ((0, 1, 2), 3))
        self.assertEqual(trace.forest.edges, ())

    def test_total_weight_overflow(self) -> None:
        graph = SpanningGraph(3, ((0, 1, (1 << 63) - 1), (1, 2, 1)))
        with self.assertRaises(OverflowError):
            kruskal_forest(graph)
        with self.assertRaises(OverflowError):
            lazy_prim_forest(graph)


class ReportingTests(unittest.TestCase):
    def test_modes_and_unknown_mode(self) -> None:
        for mode, title in (("dsu", "可追踪并查集"), ("kruskal", "Kruskal 最小生成森林"), ("prim", "Lazy Prim 最小生成森林")):
            result = subprocess.run([sys.executable, "-m", "traceable_spanning_forest_lab", mode], text=True, capture_output=True, check=True)
            self.assertTrue(result.stdout.startswith(title))
            self.assertEqual(result.stderr, "")
        failed = subprocess.run([sys.executable, "-m", "traceable_spanning_forest_lab", "bad"], text=True, capture_output=True, check=False)
        self.assertEqual((failed.returncode, failed.stdout), (2, ""))
        self.assertIn("unknown mode", failed.stderr)


if __name__ == "__main__":
    unittest.main()
