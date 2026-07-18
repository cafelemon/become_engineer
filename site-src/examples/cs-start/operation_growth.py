from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchTrace:
    index: int | None
    comparisons: int


@dataclass(frozen=True)
class GrowthRow:
    size: int
    indexed_reads: int
    missing_scan: int
    pair_comparisons: int


def linear_search(values: list[int], target: int) -> SearchTrace:
    comparisons = 0
    for index, value in enumerate(values):
        comparisons += 1
        if value == target:
            return SearchTrace(index=index, comparisons=comparisons)
    return SearchTrace(index=None, comparisons=comparisons)


def growth_row(size: int) -> GrowthRow:
    if size < 0:
        raise ValueError("size must not be negative")
    return GrowthRow(
        size=size,
        indexed_reads=1 if size > 0 else 0,
        missing_scan=size,
        pair_comparisons=size * (size - 1) // 2,
    )


def count_adjacent_increases(values: list[int]) -> tuple[int, int]:
    increases = 0
    comparisons = 0
    for index in range(1, len(values)):
        comparisons += 1
        if values[index] > values[index - 1]:
            increases += 1
    return increases, comparisons


def main() -> None:
    print("n indexed scan pairs")
    for size in (4, 8, 16, 32):
        row = growth_row(size)
        print(
            row.size,
            row.indexed_reads,
            row.missing_scan,
            row.pair_comparisons,
        )

    hours = [1, 4, 4, 7, 2]
    print("search 7:", linear_search(hours, 7))
    print("search 9:", linear_search(hours, 9))
    print("adjacent:", count_adjacent_increases(hours))


if __name__ == "__main__":
    main()

