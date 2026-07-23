from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence


@dataclass(frozen=True)
class Interval:
    label: str
    start: int
    end: int


def _validate(intervals: Sequence[Interval]) -> None:
    if any(item.end < item.start for item in intervals):
        raise ValueError("interval end must not precede start")


def earliest_finish_schedule(intervals: Sequence[Interval]) -> tuple[Interval, ...]:
    _validate(intervals)
    ordered = sorted(intervals, key=lambda item: (item.end, item.start, item.label))
    selected: list[Interval] = []
    last_end: int | None = None
    for item in ordered:
        if last_end is None or item.start >= last_end:
            selected.append(item)
            last_end = item.end
    return tuple(selected)


def earliest_start_schedule(intervals: Sequence[Interval]) -> tuple[Interval, ...]:
    _validate(intervals)
    ordered = sorted(intervals, key=lambda item: (item.start, item.end, item.label))
    selected: list[Interval] = []
    last_end: int | None = None
    for item in ordered:
        if last_end is None or item.start >= last_end:
            selected.append(item)
            last_end = item.end
    return tuple(selected)


def maximum_count_bruteforce(intervals: Sequence[Interval]) -> int:
    _validate(intervals)
    best = 0
    for size in range(len(intervals) + 1):
        for subset in combinations(intervals, size):
            ordered = sorted(subset, key=lambda item: (item.start, item.end, item.label))
            if all(ordered[index].start >= ordered[index - 1].end for index in range(1, len(ordered))):
                best = max(best, size)
    return best


def sample_intervals() -> list[Interval]:
    return [
        Interval("A", 1, 4), Interval("B", 3, 5), Interval("C", 0, 6),
        Interval("D", 5, 7), Interval("E", 3, 9), Interval("F", 5, 9),
        Interval("G", 6, 10), Interval("H", 8, 11), Interval("I", 8, 12),
        Interval("J", 2, 14), Interval("K", 12, 16),
    ]


def fixed_report() -> str:
    intervals = sample_intervals()
    ordered = sorted(intervals, key=lambda item: (item.end, item.start, item.label))
    greedy = earliest_finish_schedule(intervals)
    wrong = earliest_start_schedule(intervals)
    return "\n".join(
        [
            "intervals=A[1,4),B[3,5),C[0,6),D[5,7),E[3,9),F[5,9),G[6,10),H[8,11),I[8,12),J[2,14),K[12,16)",
            f"order_by_finish={','.join(item.label for item in ordered)}",
            f"select={','.join(item.label for item in greedy)} count={len(greedy)}",
            f"earliest_start_select={','.join(item.label for item in wrong)} count={len(wrong)}",
            "exchange=finish-no-later-preserves-room",
            "invariant=selected-intervals-nonoverlap",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())
