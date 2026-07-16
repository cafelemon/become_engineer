import io
import unittest
from contextlib import redirect_stdout
from collections.abc import Iterator
from itertools import islice
from pathlib import Path
from tempfile import TemporaryDirectory

from study_progress_reporter.analysis import (
    filter_by_tag,
    iter_by_tag,
    iter_progress_rows,
    sort_by_progress,
    summarize,
)
from study_progress_reporter.cli import main
from study_progress_reporter.fixtures import sample_records
from study_progress_reporter.instrumentation import trace_calls
from study_progress_reporter.models import StudyRecord
from study_progress_reporter.reporting import build_report, write_audit_snapshot
from study_progress_reporter.resources import staged_output_path


class ReporterTests(unittest.TestCase):
    def test_summary_handles_duplicate_tags_and_over_completion(self) -> None:
        summary = summarize(sample_records())
        self.assertEqual(summary.total_target_hours, 35.0)
        self.assertEqual(summary.total_completed_hours, 30.5)
        self.assertEqual(summary.status_counts, {"已完成": 2, "进行中": 2})
        self.assertEqual(
            summary.unique_tags,
            {"python", "cpp", "基础", "算法", "工程", "复盘"},
        )

    def test_empty_records(self) -> None:
        summary = summarize([])
        self.assertEqual(summary.total_target_hours, 0.0)
        self.assertEqual(summary.total_completed_hours, 0.0)
        self.assertEqual(summary.status_counts, {"已完成": 0, "进行中": 0})
        self.assertEqual(summary.unique_tags, set())

    def test_summary_consumes_one_shot_iterator_once(self) -> None:
        records = iter(sample_records())
        summary = summarize(records)
        self.assertEqual(summary.total_target_hours, 35.0)
        self.assertEqual(list(records), [])

    def test_sort_uses_name_as_tie_breaker_without_mutating_input(self) -> None:
        records = sample_records()
        original_names = [record.course_name for record in records]
        sorted_records = sort_by_progress(records)
        self.assertEqual(
            [record.course_name for record in sorted_records],
            ["C++ 核心", "工程复盘", "Python 起步", "算法练习"],
        )
        self.assertEqual(
            [record.course_name for record in records], original_names
        )

    def test_filter_returns_independent_copies(self) -> None:
        records = sample_records()
        filtered = filter_by_tag(records, "基础")
        self.assertEqual(
            [record.course_name for record in filtered],
            ["Python 起步", "C++ 核心", "算法练习"],
        )
        filtered[0].tags.append("changed")
        self.assertNotIn("changed", records[0].tags)

    def test_filter_missing_tag(self) -> None:
        self.assertEqual(filter_by_tag(sample_records(), "不存在"), [])

    def test_lazy_filter_does_not_run_until_next(self) -> None:
        events: list[str] = []

        def source() -> Iterator[StudyRecord]:
            events.append("start")
            for record in sample_records():
                events.append(record.course_name)
                yield record

        filtered = iter_by_tag(source(), "基础")
        self.assertEqual(events, [])
        first = next(filtered)
        self.assertEqual(first.course_name, "Python 起步")
        self.assertEqual(events, ["start", "Python 起步"])
        self.assertEqual(
            [record.course_name for record in filtered],
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
        records = [
            StudyRecord("B", 2.0, 1.0),
            StudyRecord("A", 4.0, 2.0),
        ]
        self.assertEqual(
            [record.course_name for record in sort_by_progress(records)],
            ["A", "B"],
        )

    def test_dataclass_defaults_and_object_methods(self) -> None:
        first = StudyRecord("Python", 10.0, 7.5)
        second = StudyRecord("C++", 12.0, 12.0)
        first.tags.append("基础")
        self.assertEqual(second.tags, [])
        self.assertEqual(first.progress, 0.75)
        self.assertEqual(first.status, "进行中")
        first.add_completed_hours(2.5)
        self.assertEqual(first.completed_hours, 10.0)
        self.assertEqual(first.status, "已完成")

    def test_audit_snapshot_success_and_missing_parent(self) -> None:
        records = sample_records()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            audit_path = root / "audit.txt"
            self.assertTrue(write_audit_snapshot(records, audit_path))
            self.assertEqual(
                audit_path.read_text(encoding="utf-8"),
                "学习审计快照\n"
                "Python 起步\t10\t7.5\n"
                "C++ 核心\t12\t12\n"
                "算法练习\t8\t4\n"
                "工程复盘\t5\t7\n",
            )
            audit_path.write_text("旧审计内容\n", encoding="utf-8")
            self.assertTrue(write_audit_snapshot(records, audit_path))
            self.assertTrue(
                audit_path.read_text(encoding="utf-8").startswith(
                    "学习审计快照\n"
                )
            )
            self.assertFalse(
                write_audit_snapshot(records, root / "missing" / "audit.txt")
            )

    def test_trace_calls_preserves_contract_and_metadata(self) -> None:
        events: list[str] = []

        @trace_calls(events.append)
        def join_text(left: str, right: str = "!") -> str:
            """Join two pieces of text."""

            return left + right

        self.assertEqual(join_text("完成", right="。"), "完成。")
        self.assertEqual(events, ["开始:join_text", "完成:join_text"])
        self.assertEqual(join_text.__name__, "join_text")
        self.assertEqual(join_text.__doc__, "Join two pieces of text.")
        self.assertTrue(hasattr(join_text, "__wrapped__"))

    def test_trace_calls_records_failure_without_suppressing_it(self) -> None:
        events: list[str] = []

        @trace_calls(events.append)
        def fail_export() -> None:
            raise ValueError("审计数据无效")

        with self.assertRaisesRegex(ValueError, "审计数据无效"):
            fail_export()
        self.assertEqual(
            events,
            ["开始:fail_export", "失败:fail_export:ValueError"],
        )

    def test_staged_output_preserves_old_file_and_cleans_pending_file(
        self,
    ) -> None:
        with TemporaryDirectory() as directory:
            output_path = Path(directory) / "audit.txt"
            output_path.write_text("已发布内容\n", encoding="utf-8")
            pending_path = output_path.with_name(f".{output_path.name}.tmp")

            with self.assertRaisesRegex(RuntimeError, "模拟块内失败"):
                with staged_output_path(output_path) as staged_path:
                    self.assertEqual(staged_path, pending_path)
                    staged_path.write_text("未完成内容\n", encoding="utf-8")
                    raise RuntimeError("模拟块内失败")

            self.assertEqual(
                output_path.read_text(encoding="utf-8"), "已发布内容\n"
            )
            self.assertFalse(pending_path.exists())

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
            exit_code = main(["report"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), expected + "\n")


if __name__ == "__main__":
    unittest.main()
