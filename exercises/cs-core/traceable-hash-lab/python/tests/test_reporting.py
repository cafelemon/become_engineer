import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from traceable_hash_lab.__main__ import main
from traceable_hash_lab.reporting import build_applications_report, build_hash_report, build_table_report


HASH_REPORT = """可追踪哈希实验
bucket_count=4
key | bucket | chain_before | collision
1 | 1 | 0 | no
5 | 1 | 1 | yes
9 | 1 | 2 | yes
2 | 2 | 0 | no
buckets：0=[] 1=[1, 5, 9] 2=[2] 3=[]"""

TABLE_REPORT = """分离链接哈希表
put 1=10：inserted=yes，bucket=1，comparisons=0
put 5=50：inserted=yes，bucket=1，comparisons=1
put 9=90：inserted=yes，bucket=1，comparisons=2
put 2=20：inserted=yes，bucket=2，comparisons=0
put 13=130：inserted=yes，bucket=5，comparisons=1，rehash=4->8，moved=4
get 9：value=90，bucket=1，comparisons=2
size=5，buckets=8，load_factor=0.625"""

APPLICATIONS_REPORT = """集合与频次映射
data：7, 3, 7, 9, 3
first_duplicate=7，visits=3
unique_in_order：7, 3, 9
frequencies：3=2, 7=2, 9=1"""


class ReportingTests(unittest.TestCase):
    def test_fixed_reports(self) -> None:
        self.assertEqual(build_hash_report(), HASH_REPORT)
        self.assertEqual(build_table_report(), TABLE_REPORT)
        self.assertEqual(build_applications_report(), APPLICATIONS_REPORT)

    def test_modes_default_and_unknown(self) -> None:
        for arguments, expected in [([], HASH_REPORT), (["hash"], HASH_REPORT), (["table"], TABLE_REPORT), (["applications"], APPLICATIONS_REPORT)]:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(arguments)
            self.assertEqual(code, 0)
            self.assertEqual(stdout.getvalue(), expected + "\n")
            self.assertEqual(stderr.getvalue(), "")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(["unknown"])
        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("hash|table|applications", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
