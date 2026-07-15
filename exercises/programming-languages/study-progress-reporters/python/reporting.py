from collections.abc import Iterable, Sequence

from analysis import (
    clone_record,
    iter_by_tag,
    iter_progress_rows,
    sort_by_progress,
    summarize,
)
from models import StudyRecord


def _format_names(records: Sequence[StudyRecord]) -> str:
    if not records:
        return "无"
    return ", ".join(record["course_name"] for record in records)


def build_report(records: Iterable[StudyRecord]) -> str:
    snapshot = [clone_record(record) for record in records]
    summary = summarize(snapshot)
    sorted_records = sort_by_progress(snapshot)
    basic_records = list(iter_by_tag(snapshot, "基础"))
    total_target = summary["total_target_hours"]
    overall_progress = (
        summary["total_completed_hours"] / total_target
        if total_target > 0.0
        else 0.0
    )

    lines = [
        "学习进度报告",
        f"总计划：{total_target:.1f} 小时",
        f"总完成：{summary['total_completed_hours']:.1f} 小时",
        f"总体进度：{min(max(overall_progress, 0.0), 1.0) * 100.0:.1f}%",
        "",
        "按进度排序：",
    ]

    for course_name, progress, status in iter_progress_rows(sorted_records):
        lines.append(
            f"- {course_name}：{progress * 100.0:.1f}%（{status}）"
        )

    lines.extend(["", "状态统计："])
    for status in sorted(summary["status_counts"]):
        lines.append(f"- {status}：{summary['status_counts'][status]}")

    unique_tags = ", ".join(sorted(summary["unique_tags"])) or "无"
    lines.append(f"唯一标签：{unique_tags}")
    lines.append(f"标签[基础]：{_format_names(basic_records)}")
    return "\n".join(lines)
