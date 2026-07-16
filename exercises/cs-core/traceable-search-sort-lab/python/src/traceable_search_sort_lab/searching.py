from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, init=False)
class SortedValues:
    values: tuple[int, ...]

    def __init__(self, values: Sequence[int]) -> None:
        copied = tuple(values)
        if any(left > right for left, right in zip(copied, copied[1:])):
            raise ValueError("values must be sorted in nondecreasing order")
        object.__setattr__(self, "values", copied)

    @classmethod
    def from_values(cls, values: Sequence[int]) -> SortedValues:
        return cls(values)


@dataclass(frozen=True)
class SearchTrace:
    index: int | None
    comparisons: int


@dataclass(frozen=True)
class BoundTrace:
    index: int
    comparisons: int


@dataclass(frozen=True)
class RangeTrace:
    first: int
    last: int
    comparisons: int


def linear_search(values: SortedValues, target: int) -> SearchTrace:
    comparisons = 0
    for index, value in enumerate(values.values):
        comparisons += 1
        if value == target:
            return SearchTrace(index, comparisons)
    return SearchTrace(None, comparisons)


def lower_bound(values: SortedValues, target: int) -> BoundTrace:
    left = 0
    right = len(values.values)
    comparisons = 0
    while left < right:
        middle = left + (right - left) // 2
        comparisons += 1
        if values.values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return BoundTrace(left, comparisons)


def upper_bound(values: SortedValues, target: int) -> BoundTrace:
    left = 0
    right = len(values.values)
    comparisons = 0
    while left < right:
        middle = left + (right - left) // 2
        comparisons += 1
        if values.values[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return BoundTrace(left, comparisons)


def equal_range(values: SortedValues, target: int) -> RangeTrace:
    lower = lower_bound(values, target)
    upper = upper_bound(values, target)
    return RangeTrace(lower.index, upper.index, lower.comparisons + upper.comparisons)
