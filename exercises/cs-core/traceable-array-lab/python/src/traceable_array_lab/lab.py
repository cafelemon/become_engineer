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


@dataclass(frozen=True)
class Utf8Trace:
    byte_count: int
    code_point_count: int
    ascii_count: int
    multibyte_count: int


@dataclass(frozen=True)
class GridCell:
    value: int
    flat_index: int


@dataclass(frozen=True)
class RowTrace:
    total: int
    visits: int


@dataclass(frozen=True)
class CapacityEvent:
    value: int
    size: int
    capacity: int
    copies: int
    steps: int


@dataclass(frozen=True)
class GrowthSummary:
    total_appends: int
    total_copies: int
    total_steps: int
    final_capacity: int


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


def analyze_utf8(data: bytes) -> Utf8Trace:
    text = data.decode("utf-8", errors="strict")
    ascii_count = sum(1 for value in data if value <= 0x7F)
    code_point_count = len(text)
    return Utf8Trace(
        byte_count=len(data),
        code_point_count=code_point_count,
        ascii_count=ascii_count,
        multibyte_count=code_point_count - ascii_count,
    )


def _validate_grid_shape(
    values: Sequence[int], rows: int, columns: int
) -> None:
    if rows < 0 or columns < 0:
        raise ValueError("网格行列数不能为负数")
    if rows * columns != len(values):
        raise ValueError("网格形状与数据长度不匹配")


def _grid_index(
    values: Sequence[int],
    rows: int,
    columns: int,
    row: int,
    column: int,
) -> int:
    _validate_grid_shape(values, rows, columns)
    if row < 0 or row >= rows or column < 0 or column >= columns:
        raise IndexError("网格坐标超出边界")
    return row * columns + column


def checked_grid_at(
    values: Sequence[int],
    rows: int,
    columns: int,
    row: int,
    column: int,
) -> GridCell:
    flat_index = _grid_index(values, rows, columns, row, column)
    return GridCell(value=values[flat_index], flat_index=flat_index)


def sum_grid_row(
    values: Sequence[int], rows: int, columns: int, row: int
) -> RowTrace:
    _validate_grid_shape(values, rows, columns)
    if row < 0 or row >= rows:
        raise IndexError("网格行坐标超出边界")
    start = row * columns
    total = sum(values[start : start + columns])
    return RowTrace(total=total, visits=columns)


def simulate_growth(
    values: Sequence[int], initial_capacity: int = 0
) -> list[CapacityEvent]:
    if initial_capacity < 0:
        raise ValueError("初始容量不能为负数")
    size = 0
    capacity = initial_capacity
    events: list[CapacityEvent] = []
    for value in values:
        copies = 0
        if size == capacity:
            copies = size
            capacity = 1 if capacity == 0 else capacity * 2
        size += 1
        events.append(
            CapacityEvent(
                value=value,
                size=size,
                capacity=capacity,
                copies=copies,
                steps=copies + 1,
            )
        )
    return events


def summarize_growth(events: Sequence[CapacityEvent]) -> GrowthSummary:
    return GrowthSummary(
        total_appends=len(events),
        total_copies=sum(event.copies for event in events),
        total_steps=sum(event.steps for event in events),
        final_capacity=events[-1].capacity if events else 0,
    )
