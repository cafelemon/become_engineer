from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class GridCell:
    row: int
    column: int
    flat_index: int
    value: int


@dataclass(frozen=True)
class RowTrace:
    row: int
    total: int
    visits: int


def validate_shape(values: Sequence[int], rows: int, columns: int) -> None:
    if rows < 0 or columns < 0:
        raise ValueError("rows and columns must be non-negative")
    if rows * columns != len(values):
        raise ValueError("shape does not match the number of values")


def checked_grid_at(
    values: Sequence[int],
    rows: int,
    columns: int,
    row: int,
    column: int,
) -> GridCell:
    validate_shape(values, rows, columns)
    if not 0 <= row < rows:
        raise IndexError("row is outside the grid")
    if not 0 <= column < columns:
        raise IndexError("column is outside the grid")
    flat_index = row * columns + column
    return GridCell(row, column, flat_index, values[flat_index])


def sum_grid_row(
    values: Sequence[int],
    rows: int,
    columns: int,
    row: int,
) -> RowTrace:
    validate_shape(values, rows, columns)
    if not 0 <= row < rows:
        raise IndexError("row is outside the grid")
    start = row * columns
    total = 0
    visits = 0
    for flat_index in range(start, start + columns):
        total += values[flat_index]
        visits += 1
    return RowTrace(row, total, visits)


def main() -> None:
    values = [2, 5, 3, 4, 1, 2]
    cell = checked_grid_at(values, 2, 3, 1, 2)
    row_trace = sum_grid_row(values, 2, 3, 1)
    reshaped = checked_grid_at(values, 3, 2, 2, 1)

    print("shape=2x3")
    print(
        f"coordinate=({cell.row}, {cell.column}), "
        f"flat_index={cell.flat_index}, value={cell.value}"
    )
    print(
        f"row={row_trace.row}, total={row_trace.total}, "
        f"visits={row_trace.visits}"
    )
    print(
        "same_values_as_3x2: "
        f"coordinate=({reshaped.row}, {reshaped.column}), "
        f"flat_index={reshaped.flat_index}, value={reshaped.value}"
    )


if __name__ == "__main__":
    main()
