from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class HeapMutation:
    value: int
    comparisons: int
    swaps: int
    values: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class HeapPop:
    value: int
    comparisons: int
    swaps: int
    values: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class HeapBuildTrace:
    values: tuple[int, ...]
    comparisons: int
    swaps: int


def is_min_heap(values: Iterable[int]) -> bool:
    items = tuple(values)
    return all(items[(index - 1) // 2] <= items[index] for index in range(1, len(items)))


def _sift_down(items: list[int], start: int) -> tuple[int, int]:
    comparisons = 0
    swaps = 0
    index = start
    while True:
        left = index * 2 + 1
        if left >= len(items):
            break
        right = left + 1
        child = left
        if right < len(items):
            comparisons += 1
            if items[right] < items[left]:
                child = right
        comparisons += 1
        if not items[child] < items[index]:
            break
        items[index], items[child] = items[child], items[index]
        swaps += 1
        index = child
    return comparisons, swaps


def build_min_heap(values: Iterable[int]) -> HeapBuildTrace:
    items = list(values)
    comparisons = 0
    swaps = 0
    for index in range(len(items) // 2 - 1, -1, -1):
        step_comparisons, step_swaps = _sift_down(items, index)
        comparisons += step_comparisons
        swaps += step_swaps
    return HeapBuildTrace(tuple(items), comparisons, swaps)


class TraceableMinHeap:
    def __init__(self) -> None:
        self._values: list[int] = []

    @property
    def values(self) -> tuple[int, ...]:
        return tuple(self._values)

    @property
    def size(self) -> int:
        return len(self._values)

    @property
    def empty(self) -> bool:
        return not self._values

    def push(self, value: int) -> HeapMutation:
        self._values.append(value)
        index = len(self._values) - 1
        comparisons = 0
        swaps = 0
        while index > 0:
            parent = (index - 1) // 2
            comparisons += 1
            if not self._values[index] < self._values[parent]:
                break
            self._values[index], self._values[parent] = self._values[parent], self._values[index]
            swaps += 1
            index = parent
        return HeapMutation(value, comparisons, swaps, self.values)

    def peek_min(self) -> int:
        if not self._values:
            raise IndexError("peek from empty heap")
        return self._values[0]

    def pop_min(self) -> HeapPop:
        if not self._values:
            raise IndexError("pop from empty heap")
        value = self._values[0]
        last = self._values.pop()
        comparisons = 0
        swaps = 0
        if self._values:
            self._values[0] = last
            comparisons, swaps = _sift_down(self._values, 0)
        return HeapPop(value, comparisons, swaps, self.values)
