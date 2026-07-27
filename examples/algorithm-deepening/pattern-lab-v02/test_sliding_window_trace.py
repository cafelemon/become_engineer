from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from sliding_window_trace import fixed_report, minimum_cover


class SlidingWindowTraceTests(unittest.TestCase):
    def test_canonical_minimum_cover(self) -> None:
        result = minimum_cover("ADOBECODEBANC", "ABC")
        self.assertIsNotNone(result.best)
        assert result.best is not None
        self.assertEqual((result.best.left, result.best.right, result.best.text), (9, 12, "BANC"))
        self.assertEqual(
            [item.text for item in result.improvements],
            ["ADOBEC", "EBANC", "BANC"],
        )

    def test_duplicate_requirement_uses_frequency_not_membership(self) -> None:
        result = minimum_cover("BAAC", "AAC")
        self.assertIsNotNone(result.best)
        assert result.best is not None
        self.assertEqual(result.best.text, "AAC")

    def test_no_cover_is_explicit(self) -> None:
        result = minimum_cover("ABC", "AA")
        self.assertIsNone(result.best)
        self.assertEqual(result.shrinks, 0)

    def test_empty_requirement_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty"):
            minimum_cover("ABC", "")

    def test_each_boundary_moves_at_most_text_length(self) -> None:
        text = "ADOBECODEBANC"
        result = minimum_cover(text, "ABC")
        self.assertEqual(result.expands, len(text))
        self.assertLessEqual(result.shrinks, len(text))

    def test_python_and_cpp_fixed_reports_match(self) -> None:
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("a C++20 compiler is required")
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "sliding_window_trace"
            source = Path(__file__).with_name("sliding_window_trace.cpp")
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
            run = subprocess.run(
                [str(binary)], text=True, capture_output=True, check=False, timeout=5
            )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), fixed_report())


if __name__ == "__main__":
    unittest.main()
