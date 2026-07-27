from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Mapping, Sequence


REQUIRED_FIELDS = frozenset({"sample_id", "feature_a", "feature_b", "label"})


@dataclass(frozen=True)
class Sample:
    sample_id: str
    feature_a: float | None
    feature_b: float | None
    label: int


@dataclass(frozen=True)
class QualityReport:
    rows_seen: int
    accepted: tuple[Sample, ...]
    missing_cells: int
    exact_duplicates: int
    conflicting_ids: tuple[str, ...]
    invalid_rows: int

    @property
    def status(self) -> str:
        return "reject" if self.invalid_rows or self.conflicting_ids else "review"


def _optional_number(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("feature must be numeric or missing")
    return float(value)


def _parse_row(row: Mapping[str, object]) -> Sample:
    if set(row) != REQUIRED_FIELDS:
        raise ValueError("row fields must match the schema exactly")
    sample_id = row["sample_id"]
    label = row["label"]
    if not isinstance(sample_id, str) or not sample_id.strip():
        raise ValueError("sample_id must be a non-empty string")
    if isinstance(label, bool) or not isinstance(label, int) or label not in (0, 1):
        raise ValueError("label must be integer 0 or 1")
    return Sample(
        sample_id.strip(),
        _optional_number(row["feature_a"]),
        _optional_number(row["feature_b"]),
        label,
    )


def audit_rows(rows: Sequence[Mapping[str, object]]) -> QualityReport:
    first_by_id: dict[str, Sample] = {}
    duplicate_ids: set[str] = set()
    conflict_ids: set[str] = set()
    invalid_rows = 0
    missing_cells = 0

    for raw in rows:
        try:
            sample = _parse_row(raw)
        except (TypeError, ValueError):
            invalid_rows += 1
            continue
        missing_cells += (sample.feature_a is None) + (sample.feature_b is None)
        previous = first_by_id.get(sample.sample_id)
        if previous is None:
            first_by_id[sample.sample_id] = sample
        elif previous == sample:
            duplicate_ids.add(sample.sample_id)
        else:
            conflict_ids.add(sample.sample_id)

    accepted = tuple(
        sample for sample_id, sample in sorted(first_by_id.items())
        if sample_id not in conflict_ids
    )
    return QualityReport(
        rows_seen=len(rows),
        accepted=accepted,
        missing_cells=missing_cells,
        exact_duplicates=len(duplicate_ids),
        conflicting_ids=tuple(sorted(conflict_ids)),
        invalid_rows=invalid_rows,
    )


def fixed_report() -> str:
    rows = (
        {"sample_id": "a", "feature_a": 10, "feature_b": 100, "label": 1},
        {"sample_id": "b", "feature_a": None, "feature_b": 120, "label": 0},
        {"sample_id": "a", "feature_a": 10, "feature_b": 100, "label": 1},
        {"sample_id": "c", "feature_a": 14, "feature_b": 130, "label": 1},
        {"sample_id": "c", "feature_a": 15, "feature_b": 130, "label": 1},
        {"sample_id": "d", "feature_a": 16, "feature_b": 140, "label": 2},
    )
    report = audit_rows(rows)
    return "\n".join([
        "schema=sample_id:str,feature_a:number?,feature_b:number?,label:0|1",
        f"rows_seen={report.rows_seen}",
        f"accepted_ids={','.join(sample.sample_id for sample in report.accepted)}",
        f"missing_cells={report.missing_cells}",
        f"exact_duplicates={report.exact_duplicates}",
        f"conflicting_ids={','.join(report.conflicting_ids)}",
        f"invalid_rows={report.invalid_rows}",
        f"status={report.status}",
        "invariants=explicit-schema,conflicts-not-silently-deduplicated",
    ])


if __name__ == "__main__":
    print(fixed_report())
