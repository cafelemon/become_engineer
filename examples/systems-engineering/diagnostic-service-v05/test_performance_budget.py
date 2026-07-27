from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class PerformanceBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            raise unittest.SkipTest("a C++20 compiler is required")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.binary = Path(cls.temporary.name) / "performance_budget"
        source = Path(__file__).with_name("performance_budget.cpp")
        build = subprocess.run(
            [
                compiler,
                "-std=c++20",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(source),
                "-o",
                str(cls.binary),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if build.returncode != 0:
            raise AssertionError(build.stdout + build.stderr)
        cls.result = subprocess.run(
            [str(cls.binary)], text=True, capture_output=True, check=False, timeout=5
        )
        cls.lines = cls.result.stdout.splitlines()

    def test_nearest_rank_percentiles_are_reproducible(self) -> None:
        self.assertIn("replay_samples=20", self.lines)
        self.assertIn("percentile_method=nearest-rank", self.lines)
        self.assertIn("p50_us=30", self.lines)
        self.assertIn("p95_us=120", self.lines)
        self.assertIn("p99_us=200", self.lines)

    def test_tail_budget_uses_p95_not_average(self) -> None:
        self.assertIn("budget_p95_us=150 result=pass", self.lines)

    def test_wall_clock_is_monotonic_and_observational(self) -> None:
        self.assertIn("measurement_clock=steady_clock", self.lines)
        self.assertIn("elapsed=observed-not-asserted", self.lines)

    def test_warmup_is_separate_from_measurement(self) -> None:
        self.assertIn("warmup_iterations=1000", self.lines)
        self.assertIn("measurement_samples=2000", self.lines)

    def test_program_completes_within_outer_bound(self) -> None:
        self.assertEqual(self.result.returncode, 0, self.result.stderr)


if __name__ == "__main__":
    unittest.main()
