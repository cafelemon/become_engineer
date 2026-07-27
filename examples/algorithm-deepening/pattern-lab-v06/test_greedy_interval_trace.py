from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from greedy_interval_trace import (
    Interval, earliest_finish_schedule, earliest_start_schedule,
    fixed_report, maximum_count_bruteforce, sample_intervals,
)


class GreedyIntervalTests(unittest.TestCase):
    def test_earliest_finish_matches_bruteforce_optimum(self) -> None:
        intervals = sample_intervals()
        selected = earliest_finish_schedule(intervals)
        self.assertEqual(tuple(item.label for item in selected), ("A", "D", "H", "K"))
        self.assertEqual(len(selected), maximum_count_bruteforce(intervals))

    def test_earliest_start_is_a_real_counterexample(self) -> None:
        intervals = sample_intervals()
        self.assertEqual(tuple(item.label for item in earliest_start_schedule(intervals)), ("C", "G", "K"))
        self.assertLess(len(earliest_start_schedule(intervals)), len(earliest_finish_schedule(intervals)))

    def test_touching_half_open_intervals_are_compatible(self) -> None:
        result = earliest_finish_schedule([Interval("A", 0, 2), Interval("B", 2, 3)])
        self.assertEqual(tuple(item.label for item in result), ("A", "B"))

    def test_finish_ties_are_deterministic(self) -> None:
        result = earliest_finish_schedule([Interval("B", 1, 3), Interval("A", 1, 3)])
        self.assertEqual(tuple(item.label for item in result), ("A",))

    def test_invalid_and_empty_inputs_are_explicit(self) -> None:
        self.assertEqual(earliest_finish_schedule([]), ())
        with self.assertRaises(ValueError):
            earliest_finish_schedule([Interval("bad", 3, 2)])

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("a C++20 compiler is required")
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "greedy_interval_trace"
            source = Path(__file__).with_name("greedy_interval_trace.cpp")
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
