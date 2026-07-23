from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from two_pointer_trace import find_pair, fixed_report


class TwoPointerTraceTests(unittest.TestCase):
    def test_pointer_moves_preserve_expected_trace(self) -> None:
        result, steps = find_pair([1, 2, 3, 4, 6, 8], 8)
        self.assertEqual(result, (1, 4))
        self.assertEqual([step.action for step in steps], ["right--", "left++", "match"])

    def test_no_pair_returns_none_after_bounded_scan(self) -> None:
        result, steps = find_pair([1, 2, 4, 8], 20)
        self.assertIsNone(result)
        self.assertLessEqual(len(steps), 3)

    def test_duplicate_values_keep_distinct_indices(self) -> None:
        result, _ = find_pair([2, 2, 2], 4)
        self.assertEqual(result, (0, 2))

    def test_unsorted_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "sorted"):
            find_pair([1, 3, 2], 4)

    def test_input_is_not_modified(self) -> None:
        values = [1, 2, 3, 5]
        before = values.copy()
        find_pair(values, 6)
        self.assertEqual(values, before)

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("a C++20 compiler is required")
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "two_pointer_trace"
            source = Path(__file__).with_name("two_pointer_trace.cpp")
            build = subprocess.run(
                [
                    compiler,
                    "-std=c++20",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    str(source),
                    "-o",
                    str(binary),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            result = subprocess.run(
                [str(binary)], text=True, capture_output=True, check=False, timeout=5
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), fixed_report())


if __name__ == "__main__":
    unittest.main()
