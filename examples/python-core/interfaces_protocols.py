from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, TypedDict


class StudyRecord(TypedDict):
    course_name: str
    completed_hours: float


class ReportWriter(Protocol):
    def __call__(self, report: str, /) -> None:
        ...


def build_report(
    records: Sequence[StudyRecord],
    *,
    title: str = "学习进度报告",
) -> str:
    total = sum(record["completed_hours"] for record in records)
    return f"{title}\n总完成：{total:.1f} 小时"


def run_report(
    records: Sequence[StudyRecord],
    *,
    writer: ReportWriter,
    title: str = "学习进度报告",
) -> str:
    report = build_report(records, title=title)
    writer(report)
    return report


def remember_course(
    course: str,
    history: list[str] | None = None,
) -> list[str]:
    current = [] if history is None else history
    current.append(course)
    return current


def main() -> None:
    records: list[StudyRecord] = [
        {"course_name": "Python 核心", "completed_hours": 4.0},
        {"course_name": "CS 起步", "completed_hours": 2.0},
    ]
    remembered: list[str] = []

    def print_writer(report: str, /) -> None:
        print("terminal:")
        print(report)

    def memory_writer(report: str, /) -> None:
        remembered.append(report)

    terminal_report = run_report(
        records,
        writer=print_writer,
        title="接口学习报告",
    )
    memory_report = run_report(
        records,
        writer=memory_writer,
        title="接口学习报告",
    )
    print(f"memory_count={len(remembered)}")
    print(f"memory_matches={remembered == [terminal_report] == [memory_report]}")
    first = remember_course("Python")
    second = remember_course("CS")
    print(f"fresh_defaults={first == ['Python'] and second == ['CS']}")


if __name__ == "__main__":
    main()
