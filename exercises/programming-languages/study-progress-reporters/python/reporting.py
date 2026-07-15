from collections.abc import Sequence

from analysis import (
    build_status,
    calculate_progress,
    filter_by_tag,
    sort_by_progress,
    summarize,
)
from models import StudyRecord


def _format_names(records: Sequence[StudyRecord]) -> str:
    if not records:
        return "无"
    return ", ".join(record["course_name"] for record in records)


def build_report(records: Sequence[StudyRecord]) -> str:
    summary = summarize(records)
    sorted_records = sort_by_progress(records)
    basic_records = filter_by_tag(records, "基础")
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

    for record in sorted_records:
        lines.append(
            f"- {record['course_name']}："
            f"{calculate_progress(record) * 100.0:.1f}%"
            f"（{build_status(record)}）"
        )

    lines.extend(["", "状态统计："])
    for status in sorted(summary["status_counts"]):
        lines.append(f"- {status}：{summary['status_counts'][status]}")

    unique_tags = ", ".join(sorted(summary["unique_tags"])) or "无"
    lines.append(f"唯一标签：{unique_tags}")
    lines.append(f"标签[基础]：{_format_names(basic_records)}")
    return "\n".join(lines)
