from collections.abc import Iterable, Sequence
from pathlib import Path

from study_progress_reporter.analysis import (
    clone_record,
    iter_by_tag,
    iter_progress_rows,
    sort_by_progress,
    summarize,
)
from study_progress_reporter.models import StudyRecord
from study_progress_reporter.resources import staged_output_path


def _format_names(records: Sequence[StudyRecord]) -> str:
    if not records:
        return "无"
    return ", ".join(record.course_name for record in records)


def build_report(records: Iterable[StudyRecord]) -> str:
    snapshot = [clone_record(record) for record in records]
    summary = summarize(snapshot)
    sorted_records = sort_by_progress(snapshot)
    basic_records = list(iter_by_tag(snapshot, "基础"))
    total_target = summary.total_target_hours
    overall_progress = (
        summary.total_completed_hours / total_target if total_target > 0.0 else 0.0
    )

    lines = [
        "学习进度报告",
        f"总计划：{total_target:.1f} 小时",
        f"总完成：{summary.total_completed_hours:.1f} 小时",
        f"总体进度：{min(max(overall_progress, 0.0), 1.0) * 100.0:.1f}%",
        "",
        "按进度排序：",
    ]

    for course_name, progress, status in iter_progress_rows(sorted_records):
        lines.append(f"- {course_name}：{progress * 100.0:.1f}%（{status}）")

    lines.extend(["", "状态统计："])
    for status in sorted(summary.status_counts):
        lines.append(f"- {status}：{summary.status_counts[status]}")

    unique_tags = ", ".join(sorted(summary.unique_tags)) or "无"
    lines.append(f"唯一标签：{unique_tags}")
    lines.append(f"标签[基础]：{_format_names(basic_records)}")
    return "\n".join(lines)


def write_audit_snapshot(records: Iterable[StudyRecord], output_path: Path) -> bool:
    """Write an audit snapshot without exposing a partially written file."""

    snapshot = [record.clone() for record in records]
    try:
        with staged_output_path(output_path) as pending_path:
            with pending_path.open("w", encoding="utf-8") as output:
                output.write("学习审计快照\n")
                for record in snapshot:
                    output.write(
                        f"{record.course_name}\t{record.target_hours:g}\t"
                        f"{record.completed_hours:g}\n"
                    )
    except OSError:
        return False
    return True

