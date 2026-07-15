from collections.abc import Iterable, Iterator

from models import ProgressRow, StudyRecord, StudySummary


def clone_record(record: StudyRecord) -> StudyRecord:
    return record.clone()


def calculate_progress(record: StudyRecord) -> float:
    return record.progress


def build_status(record: StudyRecord) -> str:
    return record.status


def summarize(records: Iterable[StudyRecord]) -> StudySummary:
    total_target_hours = 0.0
    total_completed_hours = 0.0
    status_counts = {"已完成": 0, "进行中": 0}
    unique_tags: set[str] = set()

    for record in records:
        total_target_hours += record.target_hours
        total_completed_hours += record.completed_hours
        status_counts[build_status(record)] += 1
        unique_tags.update(record.tags)

    return StudySummary(
        total_target_hours=total_target_hours,
        total_completed_hours=total_completed_hours,
        status_counts=status_counts,
        unique_tags=unique_tags,
    )


def sort_by_progress(records: Iterable[StudyRecord]) -> list[StudyRecord]:
    copies = [clone_record(record) for record in records]
    return sorted(
        copies,
        key=lambda record: (-calculate_progress(record), record.course_name),
    )


def iter_by_tag(
    records: Iterable[StudyRecord], tag: str
) -> Iterator[StudyRecord]:
    for record in records:
        if tag in record.tags:
            yield clone_record(record)


def filter_by_tag(
    records: Iterable[StudyRecord], tag: str
) -> list[StudyRecord]:
    return list(iter_by_tag(records, tag))


def iter_progress_rows(
    records: Iterable[StudyRecord],
) -> Iterator[ProgressRow]:
    for record in records:
        yield (
            record.course_name,
            calculate_progress(record),
            build_status(record),
        )
