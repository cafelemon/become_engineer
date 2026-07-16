import subprocess
import sys
import unittest

from traceable_tree_traversal_lab import build_frontier_report, build_recursive_report, build_shape_report


class ReportingTests(unittest.TestCase):
    def test_fixed_reports(self) -> None:
        self.assertIn("size=6，height=2，leaves=3", build_shape_report())
        self.assertIn("postorder：5, 3, 8, 11, 9, 7", build_recursive_report())
        self.assertIn("bfs_visits=6，max_frontier=3", build_frontier_report())

    def test_module_modes_and_unknown_mode(self) -> None:
        for mode, title in (("shape", "可追踪二叉树实验"), ("recursive", "递归深度优先遍历"), ("frontier", "显式前沿遍历")):
            result = subprocess.run([sys.executable, "-m", "traceable_tree_traversal_lab", mode], text=True, capture_output=True, check=False)
            self.assertEqual(0, result.returncode)
            self.assertTrue(result.stdout.startswith(title))
            self.assertEqual("", result.stderr)
        default = subprocess.run([sys.executable, "-m", "traceable_tree_traversal_lab"], text=True, capture_output=True, check=False)
        self.assertEqual(build_shape_report() + "\n", default.stdout)
        unknown = subprocess.run([sys.executable, "-m", "traceable_tree_traversal_lab", "unknown"], text=True, capture_output=True, check=False)
        self.assertEqual(2, unknown.returncode)
        self.assertEqual("", unknown.stdout)
        self.assertEqual("unknown mode: unknown\n", unknown.stderr)


if __name__ == "__main__":
    unittest.main()
