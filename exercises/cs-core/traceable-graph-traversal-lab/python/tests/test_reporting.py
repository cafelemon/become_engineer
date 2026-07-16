from __future__ import annotations

import contextlib
import io
import unittest

from traceable_graph_traversal_lab import build_bfs_report, build_dfs_report, build_graph_report
from traceable_graph_traversal_lab.__main__ import main


GRAPH_REPORT = """可追踪无向图实验
vertices=7，edges=6，adjacency_entries=12
0：[1, 2]
1：[0, 3]
2：[0, 3]
3：[1, 2, 4]
4：[3]
5：[6]
6：[5]
degrees：2, 2, 2, 3, 1, 1, 1"""

BFS_REPORT = """无权图 BFS
start=0
order：0, 1, 2, 3, 4
distances：0, 1, 1, 2, 3, unreachable, unreachable
parents：none, 0, 0, 1, 3, none, none
visits=5，edge_checks=10，max_frontier=2
path 0->4：0, 1, 3, 4，distance=3"""

DFS_REPORT = """全图 DFS
components=2
component 0：0, 1, 3, 2, 4
component 1：5, 6
visits=7，edge_checks=12，max_depth=3
cycle=yes，first_edge=(0, 2)
labels：0, 0, 0, 0, 0, 1, 1"""


class ReportingTests(unittest.TestCase):
    def test_fixed_reports(self) -> None:
        self.assertEqual(build_graph_report(), GRAPH_REPORT)
        self.assertEqual(build_bfs_report(), BFS_REPORT)
        self.assertEqual(build_dfs_report(), DFS_REPORT)

    def test_module_modes_and_unknown_mode(self) -> None:
        for mode, expected in (("graph", GRAPH_REPORT), ("bfs", BFS_REPORT), ("dfs", DFS_REPORT)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([mode]), 0)
            self.assertEqual(output.getvalue(), expected + "\n")
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            self.assertEqual(main(["unknown"]), 2)
        self.assertEqual(error.getvalue(), "unknown mode: unknown\n")


if __name__ == "__main__":
    unittest.main()
