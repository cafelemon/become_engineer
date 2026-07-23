from __future__ import annotations

import random
import subprocess
import tempfile
import unittest
from pathlib import Path

from linear_dp_trace import (
    best_non_adjacent,
    best_non_adjacent_bruteforce,
    fixed_report,
    highest_first,
)


ROOT = Path(__file__).resolve().parent


class LinearDpTests(unittest.TestCase):
    def test_sample_state_and_reconstruction(self) -> None:
        self.assertEqual(best_non_adjacent([4, 5, 4, 1, 1]), (9, (0, 2, 4), (0, 4, 5, 8, 8, 9)))

    def test_dp_matches_small_bruteforce_oracle(self) -> None:
        generator = random.Random(20260723)
        for length in range(9):
            for _ in range(20):
                values = [generator.randint(-4, 12) for _ in range(length)]
                self.assertEqual(best_non_adjacent(values)[0], best_non_adjacent_bruteforce(values))

    def test_highest_first_has_a_counterexample(self) -> None:
        self.assertEqual(highest_first([4, 5, 4, 1, 1]), (6, (1, 3)))
        self.assertEqual(best_non_adjacent([4, 5, 4, 1, 1])[0], 9)

    def test_empty_and_negative_inputs_allow_empty_choice(self) -> None:
        self.assertEqual(best_non_adjacent([]), (0, (), (0,)))
        self.assertEqual(best_non_adjacent([-5, -1, -8]), (0, (), (0, 0, 0, 0)))

    def test_ties_skip_current_deterministically(self) -> None:
        self.assertEqual(best_non_adjacent([1, 1]), (1, (0,), (0, 1, 1)))
        self.assertEqual(best_non_adjacent([2, 0, 2]), (4, (0, 2), (0, 2, 2, 4)))

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            binary = Path(temp_dir) / "linear_dp_trace"
            compile_result = subprocess.run(
                ["c++", "-std=c++20", "-Wall", "-Wextra", "-Werror", "linear_dp_trace.cpp", "-o", str(binary)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            run_result = subprocess.run([str(binary)], capture_output=True, text=True, check=False)
            self.assertEqual(run_result.returncode, 0, run_result.stderr)
            self.assertEqual(run_result.stdout.strip(), fixed_report())


if __name__ == "__main__":
    unittest.main()
