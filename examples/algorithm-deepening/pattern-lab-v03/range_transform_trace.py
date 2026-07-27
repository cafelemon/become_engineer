from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


def build_prefix(values: Sequence[int]) -> list[int]:
    prefix = [0]
    for value in values:
        prefix.append(prefix[-1] + value)
    return prefix


def range_sum(prefix: Sequence[int], left: int, right: int) -> int:
    if left < 0 or right < left or right >= len(prefix):
        raise IndexError("range must satisfy 0 <= left <= right <= n")
    return prefix[right] - prefix[left]


@dataclass(frozen=True)
class RangeAdd:
    left: int
    right: int
    delta: int


def apply_range_adds(length: int, updates: Sequence[RangeAdd]) -> tuple[list[int], list[int]]:
    if length < 0:
        raise ValueError("length must be nonnegative")
    difference = [0] * (length + 1)
    for update in updates:
        if update.left < 0 or update.right < update.left or update.right > length:
            raise IndexError("update must satisfy 0 <= left <= right <= n")
        difference[update.left] += update.delta
        difference[update.right] -= update.delta
    restored: list[int] = []
    running = 0
    for index in range(length):
        running += difference[index]
        restored.append(running)
    return difference, restored


def fixed_report() -> str:
    values = [2, -1, 3, 5, 0]
    prefix = build_prefix(values)
    updates = [
        RangeAdd(0, 3, 2),
        RangeAdd(2, 5, -1),
        RangeAdd(1, 4, 3),
    ]
    difference, restored = apply_range_adds(len(values), updates)
    return "\n".join(
        [
            "values=2,-1,3,5,0",
            f"prefix={','.join(map(str, prefix))}",
            f"sum[0:3)={range_sum(prefix, 0, 3)}",
            f"sum[1:5)={range_sum(prefix, 1, 5)}",
            f"sum[3:3)={range_sum(prefix, 3, 3)}",
            "updates=[0:3)+2,[2:5)-1,[1:4)+3",
            f"difference={','.join(map(str, difference))}",
            f"restored={','.join(map(str, restored))}",
            "invariant=half-open-boundaries-cancel",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())
