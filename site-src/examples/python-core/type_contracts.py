from __future__ import annotations

from collections.abc import Sequence
from typing import TypedDict


class StudyRecord(TypedDict):
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str]


def _string_key_mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("record must be an object")
    mapping: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError("record keys must be strings")
        mapping[key] = item
    return mapping


def _required(mapping: dict[str, object], field: str) -> object:
    if field not in mapping:
        raise ValueError(f"record is missing {field}")
    return mapping[field]


def _number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    return float(value)


def _tags(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("tags must be a list")
    result: list[str] = []
    for tag in value:
        if not isinstance(tag, str):
            raise ValueError("tags must contain only strings")
        result.append(tag)
    return result


def validate_record(value: object) -> StudyRecord:
    mapping = _string_key_mapping(value)
    course_name = _required(mapping, "course_name")
    if not isinstance(course_name, str) or not course_name.strip():
        raise ValueError("course_name must be a non-empty string")
    target_hours = _number(_required(mapping, "target_hours"), "target_hours")
    completed_hours = _number(
        _required(mapping, "completed_hours"), "completed_hours"
    )
    if target_hours <= 0.0:
        raise ValueError("target_hours must be greater than zero")
    if completed_hours < 0.0:
        raise ValueError("completed_hours must be non-negative")
    return StudyRecord(
        course_name=course_name,
        target_hours=target_hours,
        completed_hours=completed_hours,
        tags=_tags(_required(mapping, "tags")),
    )


def calculate_progress(record: StudyRecord) -> float:
    return min(record["completed_hours"] / record["target_hours"], 1.0)


def total_completed(records: Sequence[StudyRecord]) -> float:
    return sum(record["completed_hours"] for record in records)


def main() -> None:
    first_raw: object = {
        "course_name": "Python 核心",
        "target_hours": 10.0,
        "completed_hours": 4.0,
        "tags": ["python", "类型"],
    }
    second_raw: object = {
        "course_name": "CS 起步",
        "target_hours": 8.0,
        "completed_hours": 6.0,
        "tags": ["cs", "基础"],
    }
    first = validate_record(first_raw)
    second = validate_record(second_raw)

    print(f"course={first['course_name']}")
    print(f"progress={calculate_progress(first):.1%}")
    print(f"total_completed={total_completed([first, second]):.1f}")
    print(f"tuple_input={total_completed((second,)):.1f}")


if __name__ == "__main__":
    main()
