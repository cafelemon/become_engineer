import io
import unittest
from contextlib import redirect_stdout
from collections.abc import Iterator
from itertools import islice

from analysis import (
    filter_by_tag,
    iter_by_tag,
    iter_progress_rows,
    sort_by_progress,
    summarize,
)
from fixtures import sample_records
from main import main
from models import StudyRecord
from reporting import build_report


class ReporterTests(unittest.TestCase):
    def test_summary_handles_duplicate_tags_and_over_completion(self) -> None:
        summary = summarize(sample_records())
        self.assertEqual(summary["total_target_hours"], 35.0)
        self.assertEqual(summary["total_completed_hours"], 30.5)
        self.assertEqual(summary["status_counts"], {"已完成": 2, "进行中": 2})
        self.assertEqual(
            summary["unique_tags"],
            {"python", "cpp", "基础", "算法", "工程", "复盘"},
        )

    def test_empty_records(self) -> None:
        summary = summarize([])
        self.assertEqual(summary["total_target_hours"], 0.0)
        self.assertEqual(summary["total_completed_hours"], 0.0)
        self.assertEqual(summary["status_counts"], {"已完成": 0, "进行中": 0})
        self.assertEqual(summary["unique_tags"], set())

    def test_summary_consumes_one_shot_iterator_once(self) -> None:
        records = iter(sample_records())
        summary = summarize(records)
        self.assertEqual(summary["total_target_hours"], 35.0)
        self.assertEqual(list(records), [])

    def test_sort_uses_name_as_tie_breaker_without_mutating_input(self) -> None:
        records = sample_records()
        original_names = [record["course_name"] for record in records]
        sorted_records = sort_by_progress(records)
        self.assertEqual(
            [record["course_name"] for record in sorted_records],
            ["C++ 核心", "工程复盘", "Python 起步", "算法练习"],
        )
        self.assertEqual(
            [record["course_name"] for record in records], original_names
        )

    def test_filter_returns_independent_copies(self) -> None:
        records = sample_records()
        filtered = filter_by_tag(records, "基础")
        self.assertEqual(
            [record["course_name"] for record in filtered],
            ["Python 起步", "C++ 核心", "算法练习"],
        )
        filtered[0]["tags"].append("changed")
        self.assertNotIn("changed", records[0]["tags"])

    def test_filter_missing_tag(self) -> None:
        self.assertEqual(filter_by_tag(sample_records(), "不存在"), [])

    def test_lazy_filter_does_not_run_until_next(self) -> None:
        events: list[str] = []

        def source() -> Iterator[StudyRecord]:
            events.append("start")
            for record in sample_records():
                events.append(record["course_name"])
                yield record

        filtered = iter_by_tag(source(), "基础")
        self.assertEqual(events, [])
        first = next(filtered)
        self.assertEqual(first["course_name"], "Python 起步")
        self.assertEqual(events, ["start", "Python 起步"])
        self.assertEqual(
            [record["course_name"] for record in filtered],
            ["C++ 核心", "算法练习"],
        )
        self.assertEqual(list(filtered), [])

    def test_progress_rows_advance_one_record_at_a_time(self) -> None:
        rows = iter_progress_rows(sample_records())
        self.assertIs(iter(rows), rows)
        self.assertEqual(next(rows), ("Python 起步", 0.75, "进行中"))
        self.assertEqual(next(rows), ("C++ 核心", 1.0, "已完成"))
        self.assertEqual(len(list(rows)), 2)
        self.assertEqual(list(rows), [])

    def test_islice_bounds_an_infinite_generator(self) -> None:
        def natural_numbers() -> Iterator[int]:
            value = 0
            while True:
                yield value
                value += 1

        self.assertEqual(list(islice(natural_numbers(), 5)), [0, 1, 2, 3, 4])

    def test_equal_progress_uses_name_order(self) -> None:
        records: list[StudyRecord] = [
            {"course_name": "B", "target_hours": 2.0, "completed_hours": 1.0, "tags": []},
            {"course_name": "A", "target_hours": 4.0, "completed_hours": 2.0, "tags": []},
        ]
        self.assertEqual(
            [record["course_name"] for record in sort_by_progress(records)],
            ["A", "B"],
        )

    def test_report_and_main_output(self) -> None:
        expected = (
            "学习进度报告\n"
            "总计划：35.0 小时\n"
            "总完成：30.5 小时\n"
            "总体进度：87.1%\n\n"
            "按进度排序：\n"
            "- C++ 核心：100.0%（已完成）\n"
            "- 工程复盘：100.0%（已完成）\n"
            "- Python 起步：75.0%（进行中）\n"
            "- 算法练习：50.0%（进行中）\n\n"
            "状态统计：\n"
            "- 已完成：2\n"
            "- 进行中：2\n"
            "唯一标签：cpp, python, 基础, 复盘, 工程, 算法\n"
            "标签[基础]：Python 起步, C++ 核心, 算法练习"
        )
        self.assertEqual(build_report(sample_records()), expected)
        self.assertEqual(build_report(tuple(sample_records())), expected)
        self.assertEqual(build_report(iter(sample_records())), expected)
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main()
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), expected + "\n")


if __name__ == "__main__":
    unittest.main()
