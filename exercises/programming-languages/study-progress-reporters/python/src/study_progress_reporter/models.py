from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TypeAlias


ProgressRow: TypeAlias = tuple[str, float, str]


@dataclass
class StudyRecord:
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str] = field(default_factory=list)

    @property
    def progress(self) -> float:
        if self.target_hours <= 0.0:
            return 0.0
        raw_progress = self.completed_hours / self.target_hours
        return min(max(raw_progress, 0.0), 1.0)

    @property
    def status(self) -> str:
        return "已完成" if self.completed_hours >= self.target_hours else "进行中"

    def clone(self) -> StudyRecord:
        return replace(self, tags=list(self.tags))

    def add_completed_hours(self, additional_hours: float) -> None:
        self.completed_hours += additional_hours


@dataclass
class StudySummary:
    total_target_hours: float
    total_completed_hours: float
    status_counts: dict[str, int]
    unique_tags: set[str]

