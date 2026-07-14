import unittest

from reporting import build_report


class ReportingTests(unittest.TestCase):
    def test_builds_stable_report(self):
        summary = (
            10,
            8,
            ("- 函数: 50%，还需 2 小时", "- 数据结构: 100%，已完成"),
            ("Python", "数据结构"),
        )

        report = build_report(summary)

        self.assertEqual(
            report,
            "学习进度报告\n"
            "总计划：10 小时\n"
            "总完成：8 小时\n"
            "课程状态：\n"
            "- 函数: 50%，还需 2 小时\n"
            "- 数据结构: 100%，已完成\n"
            "唯一标签：Python, 数据结构\n",
        )

    def test_empty_summary_is_readable(self):
        report = build_report((0, 0, (), ()))
        self.assertIn("- 暂无记录", report)
        self.assertIn("唯一标签：无", report)


if __name__ == "__main__":
    unittest.main()

