from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchTrace:
    index: int | None
    comparisons: int


@dataclass(frozen=True)
class GrowthRow:
    size: int
    constant_steps: int
    linear_steps: int
    pair_steps: int


@dataclass(frozen=True)
class AdjacentTrace:
    increases: int
    comparisons: int


def _validate_index(values: Sequence[int], index: int) -> None:
    if index < 0 or index >= len(values):
        raise IndexError(f"索引 {index} 超出长度 {len(values)} 的序列")


def checked_at(values: Sequence[int], index: int) -> int:
    _validate_index(values, index)
    return values[index]


def replace_at_copy(values: Sequence[int], index: int, value: int) -> list[int]:
    _validate_index(values, index)
    copied = list(values)
    copied[index] = value
    return copied


def linear_search(values: Sequence[int], target: int) -> SearchTrace:
    comparisons = 0
    for index, value in enumerate(values):
        comparisons += 1
        if value == target:
            return SearchTrace(index=index, comparisons=comparisons)
    return SearchTrace(index=None, comparisons=comparisons)


def build_growth_rows(sizes: Sequence[int]) -> list[GrowthRow]:
    rows: list[GrowthRow] = []
    for size in sizes:
        if size < 0:
            raise ValueError("输入规模不能为负数")
        rows.append(
            GrowthRow(
                size=size,
                constant_steps=1 if size > 0 else 0,
                linear_steps=size,
                pair_steps=size * (size - 1) // 2,
            )
        )
    return rows


def count_adjacent_increases(values: Sequence[int]) -> AdjacentTrace:
    increases = 0
    comparisons = 0
    for index in range(1, len(values)):
        comparisons += 1
        if values[index] > values[index - 1]:
            increases += 1
    return AdjacentTrace(increases=increases, comparisons=comparisons)
