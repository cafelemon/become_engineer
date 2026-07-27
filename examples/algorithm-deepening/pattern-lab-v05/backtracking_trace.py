from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class BacktrackingResult:
    solutions: tuple[tuple[int, ...], ...]
    nodes: int
    pruned_candidates: int
    path_restored: bool


def subset_sum_combinations(values: Sequence[int], target: int) -> BacktrackingResult:
    if target < 0 or any(value <= 0 for value in values):
        raise ValueError("values must be positive and target nonnegative")
    ordered = sorted(values)
    solutions: list[tuple[int, ...]] = []
    path: list[int] = []
    nodes = 0
    pruned = 0

    def search(start: int, total: int) -> None:
        nonlocal nodes, pruned
        nodes += 1
        if total == target:
            solutions.append(tuple(path))
            return
        for index in range(start, len(ordered)):
            if index > start and ordered[index] == ordered[index - 1]:
                pruned += 1
                continue
            candidate = ordered[index]
            if total + candidate > target:
                pruned += len(ordered) - index
                break
            path.append(candidate)
            search(index + 1, total + candidate)
            path.pop()

    search(0, 0)
    return BacktrackingResult(tuple(solutions), nodes, pruned, path == [])


def fixed_report() -> str:
    result = subset_sum_combinations([2, 3, 5, 6, 7], 10)
    lines = ["values=2,3,5,6,7 target=10"]
    lines.extend(f"solution={','.join(map(str, item))}" for item in result.solutions)
    lines.extend(
        [
            f"solutions={len(result.solutions)}",
            f"nodes={result.nodes} pruned_candidates={result.pruned_candidates}",
            f"path_after_search={'empty' if result.path_restored else 'dirty'}",
            "invariant=choose-search-undo",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(fixed_report())
