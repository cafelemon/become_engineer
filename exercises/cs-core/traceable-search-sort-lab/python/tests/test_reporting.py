import contextlib
import io
import unittest

from traceable_search_sort_lab.__main__ import main
from traceable_search_sort_lab.reporting import (
    build_elementary_report,
    build_merge_report,
    build_search_report,
)


SEARCH_REPORT = """有序查找实验
data：1, 3, 3, 3, 7, 9
target=3
linear：index=1，comparisons=2
lower_bound：index=1，comparisons=3
upper_bound：index=4，comparisons=3
equal_range：[1, 4)"""

ELEMENTARY_REPORT = """基础比较排序
data：3A, 1B, 3C, 2D
insertion：1B, 2D, 3A, 3C
comparisons=5，shifts=3，stable=yes
selection：1B, 2D, 3C, 3A
comparisons=6，swaps=2，stable=no"""

MERGE_REPORT = """迭代归并排序
data：3A, 1B, 3C, 2D
width=1：1B, 3A | 2D, 3C
width=2：1B, 2D, 3A, 3C
comparisons=5，writes=8，passes=2
stable=yes，input_unchanged=yes"""


class ReportingTests(unittest.TestCase):
    def test_reports_match_contract(self) -> None:
        self.assertEqual(build_search_report(), SEARCH_REPORT)
        self.assertEqual(build_elementary_report(), ELEMENTARY_REPORT)
        self.assertEqual(build_merge_report(), MERGE_REPORT)

    def test_default_and_each_mode(self) -> None:
        for arguments, expected in [
            ([], SEARCH_REPORT),
            (["search"], SEARCH_REPORT),
            (["elementary"], ELEMENTARY_REPORT),
            (["merge"], MERGE_REPORT),
        ]:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main(arguments), 0)
            self.assertEqual(stdout.getvalue(), expected + "\n")

    def test_unknown_mode_only_uses_stderr_and_returns_two(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(main(["unknown"]), 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("search|elementary|merge", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
