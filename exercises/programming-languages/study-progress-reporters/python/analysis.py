from collections.abc import Sequence

from models import StudyRecord, StudySummary


def clone_record(record: StudyRecord) -> StudyRecord:
    return {
        "course_name": record["course_name"],
        "target_hours": record["target_hours"],
        "completed_hours": record["completed_hours"],
        "tags": list(record["tags"]),
    }


def calculate_progress(record: StudyRecord) -> float:
    if record["target_hours"] <= 0.0:
        return 0.0
    raw_progress = record["completed_hours"] / record["target_hours"]
    return min(max(raw_progress, 0.0), 1.0)


def build_status(record: StudyRecord) -> str:
    return (
        "已完成"
        if record["completed_hours"] >= record["target_hours"]
        else "进行中"
    )


def summarize(records: Sequence[StudyRecord]) -> StudySummary:
    status_counts = {"已完成": 0, "进行中": 0}
    unique_tags: set[str] = set()

    for record in records:
        status_counts[build_status(record)] += 1
        unique_tags.update(record["tags"])

    return {
        "total_target_hours": sum(record["target_hours"] for record in records),
        "total_completed_hours": sum(
            record["completed_hours"] for record in records
        ),
        "status_counts": status_counts,
        "unique_tags": unique_tags,
    }


def sort_by_progress(records: Sequence[StudyRecord]) -> list[StudyRecord]:
    copies = [clone_record(record) for record in records]
    return sorted(
        copies,
        key=lambda record: (-calculate_progress(record), record["course_name"]),
    )


def filter_by_tag(
    records: Sequence[StudyRecord], tag: str
) -> list[StudyRecord]:
    return [
        clone_record(record) for record in records if tag in record["tags"]
    ]
