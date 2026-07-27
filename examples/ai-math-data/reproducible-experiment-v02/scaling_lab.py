from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Sequence


def _shape(rows: Sequence[Sequence[float]]) -> int:
    if not rows:
        raise ValueError("training rows must not be empty")
    columns = len(rows[0])
    if columns == 0 or any(len(row) != columns for row in rows):
        raise ValueError("rows must be a non-empty rectangular table")
    return columns


@dataclass(frozen=True)
class Standardizer:
    means: tuple[float, ...]
    scales: tuple[float, ...]

    def transform(self, rows: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], ...]:
        if any(len(row) != len(self.means) for row in rows):
            raise ValueError("transform shape must match fitted columns")
        return tuple(
            tuple((value - mean) / scale for value, mean, scale in zip(row, self.means, self.scales, strict=True))
            for row in rows
        )


def fit_standardizer(training_rows: Sequence[Sequence[float]]) -> Standardizer:
    columns = _shape(training_rows)
    means = tuple(sum(row[index] for row in training_rows) / len(training_rows) for index in range(columns))
    variances = tuple(
        sum((row[index] - means[index]) ** 2 for row in training_rows) / len(training_rows)
        for index in range(columns)
    )
    scales = tuple(sqrt(variance) for variance in variances)
    if any(scale == 0 for scale in scales):
        raise ValueError("constant columns must be removed or handled explicitly")
    return Standardizer(means, scales)


def distance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("points must have the same dimension")
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def fixed_report() -> str:
    rows = ((2.0, 10.0), (4.0, 20.0), (6.0, 30.0), (8.0, 40.0))
    fitted = fit_standardizer(rows)
    transformed = fitted.transform(rows)
    return "\n".join([
        "rows=2,10;4,20;6,30;8,40",
        f"means={','.join(f'{value:.3f}' for value in fitted.means)}",
        f"scales={','.join(f'{value:.3f}' for value in fitted.scales)}",
        f"z_first={','.join(f'{value:.3f}' for value in transformed[0])}",
        f"z_last={','.join(f'{value:.3f}' for value in transformed[-1])}",
        f"raw_distance_first_last={distance(rows[0], rows[-1]):.3f}",
        f"z_distance_first_last={distance(transformed[0], transformed[-1]):.3f}",
        "constant=reject",
        "invariants=train-fit-only,nonzero-scale",
    ])


if __name__ == "__main__":
    print(fixed_report())

