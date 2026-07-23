from __future__ import annotations

import unittest

from data_quality_lab import audit_rows, fixed_report


def row(sample_id: str, feature_a: object, feature_b: object, label: object) -> dict[str, object]:
    return {"sample_id": sample_id, "feature_a": feature_a, "feature_b": feature_b, "label": label}


class DataQualityLabTests(unittest.TestCase):
    def test_valid_rows_are_normalized_and_sorted(self) -> None:
        report = audit_rows((row("b", 2, 3.5, 0), row("a", 1, 2, 1)))
        self.assertEqual([sample.sample_id for sample in report.accepted], ["a", "b"])
        self.assertEqual(report.accepted[0].feature_a, 1.0)

    def test_missing_features_are_counted_not_coerced(self) -> None:
        report = audit_rows((row("a", None, 2, 1), row("b", 3, None, 0)))
        self.assertEqual(report.missing_cells, 2)
        self.assertIsNone(report.accepted[0].feature_a)

    def test_exact_duplicates_are_counted_once(self) -> None:
        same = row("a", 1, 2, 1)
        report = audit_rows((same, same, same))
        self.assertEqual(report.exact_duplicates, 1)
        self.assertEqual(len(report.accepted), 1)

    def test_conflicting_identifier_removes_the_ambiguous_sample(self) -> None:
        report = audit_rows((row("a", 1, 2, 1), row("a", 9, 2, 1), row("b", 3, 4, 0)))
        self.assertEqual(report.conflicting_ids, ("a",))
        self.assertEqual([sample.sample_id for sample in report.accepted], ["b"])
        self.assertEqual(report.status, "reject")

    def test_schema_type_and_label_errors_are_rejected(self) -> None:
        rows = (
            {"sample_id": "a", "feature_a": 1, "label": 1},
            row("", 1, 2, 1),
            row("b", True, 2, 0),
            row("c", 1, 2, 2),
        )
        report = audit_rows(rows)
        self.assertEqual(report.invalid_rows, 4)
        self.assertEqual(report.accepted, ())

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("accepted_ids=a,b", report)
        self.assertIn("missing_cells=1", report)
        self.assertIn("conflicting_ids=c", report)
        self.assertTrue(report.endswith("invariants=explicit-schema,conflicts-not-silently-deduplicated"))


if __name__ == "__main__":
    unittest.main()
