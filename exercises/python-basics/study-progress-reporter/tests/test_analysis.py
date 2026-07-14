import unittest

from analysis import calculate_progress, summarize_records


class AnalysisTests(unittest.TestCase):
    def test_summarizes_normal_records_and_removes_duplicate_tags(self):
        records = [
            {
                "course": "函数",
                "target_hours": 4,
                "finished_hours": 2,
                "tags": ["Python", "编程"],
            },
            {
                "course": "数据结构",
                "target_hours": 6,
                "finished_hours": 6,
                "tags": ["Python", "数据结构"],
            },
        ]

        summary = summarize_records(records)

        self.assertEqual(summary[0], 10)
        self.assertEqual(summary[1], 8)
        self.assertEqual(
            summary[2],
            ("- 函数: 50%，还需 2 小时", "- 数据结构: 100%，已完成"),
        )
        self.assertEqual(summary[3], ("Python", "数据结构", "编程"))

    def test_empty_records_have_zero_totals(self):
        self.assertEqual(summarize_records([]), (0, 0, (), ()))

    def test_progress_is_capped_for_over_completion(self):
        self.assertEqual(calculate_progress(2, 3), 1.0)


if __name__ == "__main__":
    unittest.main()

