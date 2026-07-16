from __future__ import annotations

import subprocess
import sys
import unittest

from traceable_array_lab import build_report


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


if __name__ == "__main__":
    unittest.main()
