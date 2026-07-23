from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Step:
    left: int
    right: int
    total: int
    action: str


def find_pair(values: Sequence[int], target: int) -> tuple[tuple[int, int] | None, list[Step]]:
    if any(values[index] > values[index + 1] for index in range(len(values) - 1)):
        raise ValueError("values must be sorted in nondecreasing order")
    left, right = 0, len(values) - 1
    steps: list[Step] = []
    while left < right:
        total = values[left] + values[right]
        if total == target:
            steps.append(Step(left, right, total, "match"))
            return (left, right), steps
        if total < target:
            steps.append(Step(left, right, total, "left++"))
            left += 1
        else:
            steps.append(Step(left, right, total, "right--"))
            right -= 1
    return None, steps


def fixed_report() -> str:
    values = [1, 2, 3, 4, 6, 8]
    result, steps = find_pair(values, 8)
    lines = ["input=1,2,3,4,6,8 target=8"]
    lines.extend(
        f"step left={step.left} right={step.right} sum={step.total} action={step.action}"
        for step in steps
    )
    if result is None:
        lines.append("result=not-found")
    else:
        left, right = result
        lines.append(
            f"result={left},{right} values={values[left]},{values[right]}"
        )
    lines.append("invariant=outside-pairs-eliminated")
    return "\n".join(lines)


if __name__ == "__main__":
    print(fixed_report())
