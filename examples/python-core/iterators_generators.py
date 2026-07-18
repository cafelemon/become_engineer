from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import islice
from typing import TypedDict


class StudyRecord(TypedDict):
    course_name: str
    completed_hours: float
    target_hours: float
    tags: list[str]


def iter_by_tag(
    records: Iterable[StudyRecord], tag: str
) -> Iterator[StudyRecord]:
    for record in records:
        if tag in record["tags"]:
            yield record


def one_pass_summary(values: Iterable[float]) -> tuple[float, int]:
    total = 0.0
    count = 0
    for value in values:
        total += value
        count += 1
    return total, count


def natural_numbers() -> Iterator[int]:
    value = 0
    while True:
        yield value
        value += 1


def main() -> None:
    events: list[str] = []

    def source() -> Iterator[StudyRecord]:
        events.append("start")
        for record in (
            StudyRecord(
                course_name="Python",
                completed_hours=4.0,
                target_hours=10.0,
                tags=["基础"],
            ),
            StudyRecord(
                course_name="Web",
                completed_hours=1.0,
                target_hours=8.0,
                tags=["应用"],
            ),
            StudyRecord(
                course_name="CS",
                completed_hours=6.0,
                target_hours=8.0,
                tags=["基础"],
            ),
        ):
            events.append(record["course_name"])
            yield record

    filtered = iter_by_tag(source(), "基础")
    print(f"before={events}")
    first = next(filtered)
    print(f"first={first['course_name']}")
    print(f"after_first={events}")
    print(f"remaining={[record['course_name'] for record in filtered]}")
    print(f"exhausted={list(filtered)}")
    print(f"one_pass={one_pass_summary(iter([4.0, 6.0]))}")
    print(f"bounded={list(islice(natural_numbers(), 5))}")


if __name__ == "__main__":
    main()
