from __future__ import annotations

import subprocess
import sys
import unittest

from traceable_array_lab import (
    build_capacity_report,
    build_grid_report,
    build_report,
    build_text_report,
)


EXPECTED_REPORT = """可追踪数组实验
数据：7, 3, 9, 3
index=2：9
target=3：index=1，comparisons=2

增长表
n | 常量访问 | 线性扫描 | 两两比较
4 | 1 | 4 | 6
8 | 1 | 8 | 28
16 | 1 | 16 | 120
32 | 1 | 32 | 496"""

EXPECTED_MODES = {
    "text": """UTF-8 扫描
text：A工🧪
bytes=8，code_points=3
ascii=1，multibyte=2""",
    "grid": """二维网格
shape=2x3
data：1, 2, 3 / 4, 5, 6
row=1，col=2：value=6，flat_index=5
row=0：sum=6，visits=3""",
    "capacity": """动态数组扩容
append | size | capacity | copies | steps
7 | 1 | 1 | 0 | 1
3 | 2 | 2 | 1 | 2
9 | 3 | 4 | 2 | 3
3 | 4 | 4 | 0 | 1
5 | 5 | 8 | 4 | 5
total_steps=12""",
}


class ReportingTests(unittest.TestCase):
    def test_report_contract(self) -> None:
        self.assertEqual(build_report(), EXPECTED_REPORT)

    def test_module_entrypoint(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "traceable_array_lab"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, EXPECTED_REPORT + "\n")
        self.assertEqual(result.stderr, "")

    def test_explicit_report_builders(self) -> None:
        self.assertEqual(build_text_report(), EXPECTED_MODES["text"])
        self.assertEqual(build_grid_report(), EXPECTED_MODES["grid"])
        self.assertEqual(build_capacity_report(), EXPECTED_MODES["capacity"])

    def test_all_explicit_module_modes(self) -> None:
        for mode, expected in {"baseline": EXPECTED_REPORT, **EXPECTED_MODES}.items():
            with self.subTest(mode=mode):
                result = subprocess.run(
                    [sys.executable, "-m", "traceable_array_lab", mode],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, expected + "\n")
                self.assertEqual(result.stderr, "")

    def test_unknown_mode_is_argparse_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "traceable_array_lab", "unknown"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
