from __future__ import annotations

import random
import subprocess
import tempfile
import unittest
from pathlib import Path

from structured_dp_trace import (
    fixed_report,
    knapsack_01,
    knapsack_bruteforce,
    knapsack_forward_wrong,
    matrix_chain,
)


ROOT = Path(__file__).resolve().parent


class StructuredDpTests(unittest.TestCase):
    def test_knapsack_fixed_capacity_table(self) -> None:
        self.assertEqual(knapsack_01([2, 3, 4, 5], [3, 4, 5, 8], 7), (0, 0, 3, 4, 5, 8, 8, 11))

    def test_descending_capacity_prevents_same_item_reuse(self) -> None:
        self.assertEqual(knapsack_01([2], [3], 4)[-1], 3)
        self.assertEqual(knapsack_forward_wrong([2], [3], 4)[-1], 6)

    def test_knapsack_matches_small_bruteforce_oracle(self) -> None:
        generator = random.Random(20260723)
        for item_count in range(6):
            for _ in range(20):
                weights = [generator.randint(1, 5) for _ in range(item_count)]
                values = [generator.randint(-2, 9) for _ in range(item_count)]
                capacity = generator.randint(0, 10)
                self.assertEqual(knapsack_01(weights, values, capacity)[-1], knapsack_bruteforce(weights, values, capacity))

    def test_matrix_chain_uses_shorter_intervals_first(self) -> None:
        self.assertEqual(matrix_chain([10, 30, 5, 60]), (4500, "((A1A2)A3)"))
        self.assertEqual(matrix_chain([5, 10]), (0, "A1"))

    def test_invalid_inputs_are_rejected(self) -> None:
        for call in (
            lambda: knapsack_01([1], [], 2),
            lambda: knapsack_01([0], [1], 2),
            lambda: knapsack_01([], [], -1),
            lambda: matrix_chain([10]),
            lambda: matrix_chain([10, 0]),
        ):
            with self.assertRaises(ValueError):
                call()

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            binary = Path(temp_dir) / "structured_dp_trace"
            compile_result = subprocess.run(
                ["c++", "-std=c++20", "-Wall", "-Wextra", "-Werror", "structured_dp_trace.cpp", "-o", str(binary)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            run_result = subprocess.run([str(binary)], capture_output=True, text=True, check=False)
            self.assertEqual(run_result.returncode, 0, run_result.stderr)
            self.assertEqual(run_result.stdout.strip(), fixed_report())


if __name__ == "__main__":
    unittest.main()

