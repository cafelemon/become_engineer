from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class TaggedValue:
    key: int
    tag: str


@dataclass(frozen=True)
class InsertionSortTrace:
    items: tuple[TaggedValue, ...]
    comparisons: int
    shifts: int


@dataclass(frozen=True)
class SelectionSortTrace:
    items: tuple[TaggedValue, ...]
    comparisons: int
    swaps: int


@dataclass(frozen=True)
class MergeTrace:
    items: tuple[TaggedValue, ...]
    comparisons: int
    writes: int


@dataclass(frozen=True)
class MergePass:
    width: int
    items: tuple[TaggedValue, ...]


@dataclass(frozen=True)
class MergeSortTrace:
    items: tuple[TaggedValue, ...]
    comparisons: int
    writes: int
    passes: tuple[MergePass, ...]


def _comes_before(left: TaggedValue, right: TaggedValue, descending: bool) -> bool:
    return left.key > right.key if descending else left.key < right.key


def insertion_sort(
    values: Sequence[TaggedValue], *, descending: bool = False
) -> InsertionSortTrace:
    items = list(values)
    comparisons = 0
    shifts = 0
    for current_index in range(1, len(items)):
        current = items[current_index]
        position = current_index
        while position > 0:
            comparisons += 1
            if not _comes_before(current, items[position - 1], descending):
                break
            items[position] = items[position - 1]
            shifts += 1
            position -= 1
        items[position] = current
    return InsertionSortTrace(tuple(items), comparisons, shifts)


def selection_sort(
    values: Sequence[TaggedValue], *, descending: bool = False
) -> SelectionSortTrace:
    items = list(values)
    comparisons = 0
    swaps = 0
    for start in range(len(items)):
        selected = start
        for candidate in range(start + 1, len(items)):
            comparisons += 1
            if _comes_before(items[candidate], items[selected], descending):
                selected = candidate
        if selected != start:
            items[start], items[selected] = items[selected], items[start]
            swaps += 1
    return SelectionSortTrace(tuple(items), comparisons, swaps)


def preserves_equal_order(
    original: Sequence[TaggedValue], result: Sequence[TaggedValue]
) -> bool:
    keys = {item.key for item in original}
    return all(
        [item.tag for item in original if item.key == key]
        == [item.tag for item in result if item.key == key]
        for key in keys
    )


def merge_sorted(
    left: Sequence[TaggedValue],
    right: Sequence[TaggedValue],
    *,
    descending: bool = False,
) -> MergeTrace:
    merged: list[TaggedValue] = []
    left_index = 0
    right_index = 0
    comparisons = 0
    while left_index < len(left) and right_index < len(right):
        comparisons += 1
        if _comes_before(right[right_index], left[left_index], descending):
            merged.append(right[right_index])
            right_index += 1
        else:
            merged.append(left[left_index])
            left_index += 1
    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return MergeTrace(tuple(merged), comparisons, len(merged))


def bottom_up_merge_sort(
    values: Sequence[TaggedValue], *, descending: bool = False
) -> MergeSortTrace:
    items = list(values)
    width = 1
    comparisons = 0
    writes = 0
    passes: list[MergePass] = []
    while width < len(items):
        next_items: list[TaggedValue] = []
        for start in range(0, len(items), width * 2):
            merged = merge_sorted(
                items[start : start + width],
                items[start + width : start + width * 2],
                descending=descending,
            )
            next_items.extend(merged.items)
            comparisons += merged.comparisons
            writes += merged.writes
        items = next_items
        passes.append(MergePass(width, tuple(items)))
        width *= 2
    return MergeSortTrace(tuple(items), comparisons, writes, tuple(passes))
