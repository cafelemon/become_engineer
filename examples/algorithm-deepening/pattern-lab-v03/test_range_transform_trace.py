from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from range_transform_trace import (
    RangeAdd,
    apply_range_adds,
    build_prefix,
    fixed_report,
    range_sum,
)


class RangeTransformTraceTests(unittest.TestCase):
    def test_prefix_queries_use_half_open_bounds(self) -> None:
        prefix = build_prefix([2, -1, 3, 5, 0])
        self.assertEqual(prefix, [0, 2, 1, 4, 9, 9])
        self.assertEqual(range_sum(prefix, 0, 3), 4)
        self.assertEqual(range_sum(prefix, 1, 5), 7)

    def test_empty_range_sum_is_zero(self) -> None:
        self.assertEqual(range_sum(build_prefix([4, 5]), 1, 1), 0)

    def test_invalid_query_is_rejected(self) -> None:
        prefix = build_prefix([1, 2])
        with self.assertRaises(IndexError):
            range_sum(prefix, 2, 1)
        with self.assertRaises(IndexError):
            range_sum(prefix, 0, 3)

    def test_overlapping_range_adds_restore_expected_values(self) -> None:
        difference, restored = apply_range_adds(
            5,
            [RangeAdd(0, 3, 2), RangeAdd(2, 5, -1), RangeAdd(1, 4, 3)],
        )
        self.assertEqual(difference, [2, 3, -1, -2, -3, 1])
        self.assertEqual(restored, [2, 5, 4, 2, -1])

    def test_empty_update_has_no_effect(self) -> None:
        _, restored = apply_range_adds(3, [RangeAdd(1, 1, 99)])
        self.assertEqual(restored, [0, 0, 0])

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("a C++20 compiler is required")
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "range_transform_trace"
            source = Path(__file__).with_name("range_transform_trace.cpp")
            build = subprocess.run(
                [compiler, "-std=c++20", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(binary)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            run = subprocess.run([str(binary)], text=True, capture_output=True, check=False, timeout=5)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), fixed_report())


if __name__ == "__main__":
    unittest.main()
