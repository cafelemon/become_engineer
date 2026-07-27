from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class NextGreaterResult:
    answers: tuple[int | None, ...]
    resolved: int
    unresolved: int


def next_strictly_greater(values: Sequence[int]) -> NextGreaterResult:
    answers: list[int | None] = [None] * len(values)
    stack: list[int] = []
    resolved = 0
    for index, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            answers[stack.pop()] = value
            resolved += 1
        stack.append(index)
    return NextGreaterResult(tuple(answers), resolved, len(stack))


@dataclass(frozen=True)
class WindowMaximumResult:
    maxima: tuple[int, ...]
    back_pruned: int
    expired: int


def sliding_maximum(values: Sequence[int], width: int) -> WindowMaximumResult:
    if width <= 0:
        raise ValueError("width must be positive")
    if width > len(values):
        return WindowMaximumResult((), 0, 0)
    candidates: deque[int] = deque()
    maxima: list[int] = []
    back_pruned = 0
    expired = 0
    for index, value in enumerate(values):
        while candidates and candidates[0] <= index - width:
            candidates.popleft()
            expired += 1
        while candidates and values[candidates[-1]] <= value:
            candidates.pop()
            back_pruned += 1
        candidates.append(index)
        if index + 1 >= width:
            maxima.append(values[candidates[0]])
    return WindowMaximumResult(tuple(maxima), back_pruned, expired)


def fixed_report() -> str:
    values = [2, 1, 2, 4, 3]
    greater = next_strictly_greater(values)
    maximum = sliding_maximum(values, 3)
    answers = ",".join("none" if item is None else str(item) for item in greater.answers)
    return "\n".join(
        [
            "values=2,1,2,4,3",
            f"next_strictly_greater={answers}",
            f"stack_resolved={greater.resolved} unresolved={greater.unresolved}",
            "window_width=3",
            f"window_maxima={','.join(map(str, maximum.maxima))}",
            f"deque_back_pruned={maximum.back_pruned} expired={maximum.expired}",
            "invariant=dominated-candidates-never-return",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())
