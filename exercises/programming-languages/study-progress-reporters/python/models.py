from typing import TypedDict


class StudyRecord(TypedDict):
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str]


class StudySummary(TypedDict):
    total_target_hours: float
    total_completed_hours: float
    status_counts: dict[str, int]
    unique_tags: set[str]
