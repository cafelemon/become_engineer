from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from monotonic_structures_trace import (
    fixed_report,
    next_strictly_greater,
    sliding_maximum,
)


class MonotonicStructuresTests(unittest.TestCase):
    def test_next_strictly_greater_keeps_equal_values_unresolved(self) -> None:
        result = next_strictly_greater([2, 1, 2, 4, 3])
        self.assertEqual(result.answers, (4, 2, 4, None, None))
        self.assertEqual((result.resolved, result.unresolved), (3, 2))

    def test_decreasing_input_has_no_next_greater(self) -> None:
        result = next_strictly_greater([4, 3, 2, 1])
        self.assertEqual(result.answers, (None, None, None, None))

    def test_sliding_maximum_uses_candidate_front(self) -> None:
        result = sliding_maximum([2, 1, 2, 4, 3], 3)
        self.assertEqual(result.maxima, (2, 4, 4))
        self.assertEqual(result.back_pruned, 3)

    def test_expired_maximum_is_removed(self) -> None:
        result = sliding_maximum([9, 1, 2, 3], 2)
        self.assertEqual(result.maxima, (9, 2, 3))
        self.assertGreaterEqual(result.expired, 1)

    def test_invalid_and_oversized_widths_are_explicit(self) -> None:
        with self.assertRaises(ValueError):
            sliding_maximum([1], 0)
        self.assertEqual(sliding_maximum([1, 2], 3).maxima, ())

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("a C++20 compiler is required")
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "monotonic_structures_trace"
            source = Path(__file__).with_name("monotonic_structures_trace.cpp")
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
