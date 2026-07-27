from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from backtracking_trace import fixed_report, subset_sum_combinations


class BacktrackingTraceTests(unittest.TestCase):
    def test_target_combinations_are_deterministic(self) -> None:
        result = subset_sum_combinations([2, 3, 5, 6, 7], 10)
        self.assertEqual(result.solutions, ((2, 3, 5), (3, 7)))

    def test_duplicate_input_does_not_duplicate_solution(self) -> None:
        result = subset_sum_combinations([1, 1, 2], 3)
        self.assertEqual(result.solutions, ((1, 2),))

    def test_no_solution_is_explicit(self) -> None:
        self.assertEqual(subset_sum_combinations([2, 4], 3).solutions, ())

    def test_empty_combination_solves_zero_target(self) -> None:
        self.assertEqual(subset_sum_combinations([1, 2], 0).solutions, ((),))

    def test_state_is_restored_and_invalid_values_rejected(self) -> None:
        self.assertTrue(subset_sum_combinations([2, 3], 5).path_restored)
        with self.assertRaises(ValueError):
            subset_sum_combinations([0, 2], 2)

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("a C++20 compiler is required")
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "backtracking_trace"
            source = Path(__file__).with_name("backtracking_trace.cpp")
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
