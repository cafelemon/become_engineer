from __future__ import annotations

from math import sqrt
from typing import Sequence


def dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have the same length")
    return sum(a * b for a, b in zip(left, right, strict=True))


def matrix_shape(matrix: Sequence[Sequence[float]]) -> tuple[int, int]:
    if not matrix:
        return 0, 0
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix must be rectangular")
    return len(matrix), columns


def matrix_vector(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> tuple[float, ...]:
    _, columns = matrix_shape(matrix)
    if columns != len(vector):
        raise ValueError("matrix columns must match vector length")
    return tuple(dot(row, vector) for row in matrix)


def euclidean_distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("points must have the same dimension")
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def fixed_report() -> str:
    vector = (1.0, 2.0, 3.0)
    weights = (0.5, -1.0, 2.0)
    matrix = ((1.0, 2.0, 3.0), (2.0, 0.0, 1.0))
    rows, columns = matrix_shape(matrix)
    transformed = matrix_vector(matrix, weights)
    return "\n".join([
        "vector=1,2,3 weights=0.5,-1,2",
        f"dot={dot(vector, weights):.1f}",
        f"matrix_shape={rows}x{columns}",
        f"matvec={','.join(f'{value:.1f}' for value in transformed)}",
        f"distance_0_0_to_3_4={euclidean_distance((0, 0), (3, 4)):.1f}",
        "ragged=reject",
        "invariants=same-length,rectangular-shape",
    ])


if __name__ == "__main__":
    print(fixed_report())

