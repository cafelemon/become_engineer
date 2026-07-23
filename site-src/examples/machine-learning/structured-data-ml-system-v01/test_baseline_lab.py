from __future__ import annotations

import unittest

import pandas as pd

from baseline_lab import (
    EXPECTED_COLUMNS,
    FEATURE_COLUMNS,
    build_dataset,
    evaluate_most_frequent_baseline,
    fixed_report,
    split_dataset,
    validate_dataset,
)


class BaselineLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = build_dataset()

    def test_dataset_has_explicit_schema_and_binary_target(self) -> None:
        validate_dataset(self.frame)
        self.assertEqual(tuple(self.frame.columns), EXPECTED_COLUMNS)
        self.assertEqual(set(self.frame["target"]), {0, 1})
        self.assertEqual(len(self.frame), 120)

    def test_generation_is_reproducible_but_seed_sensitive(self) -> None:
        pd.testing.assert_frame_equal(build_dataset(7), build_dataset(7))
        self.assertFalse(build_dataset(7).equals(build_dataset(8)))

    def test_split_is_stratified_without_overlap_or_loss(self) -> None:
        split = split_dataset(self.frame)
        self.assertEqual(split.y_train.value_counts().sort_index().to_dict(), {0: 60, 1: 30})
        self.assertEqual(split.y_validation.value_counts().sort_index().to_dict(), {0: 20, 1: 10})
        self.assertFalse(set(split.train_ids) & set(split.validation_ids))
        self.assertEqual(set(split.train_ids) | set(split.validation_ids), set(self.frame["sample_id"]))

    def test_target_and_identifier_are_excluded_from_features(self) -> None:
        split = split_dataset(self.frame)
        self.assertEqual(tuple(split.x_train.columns), FEATURE_COLUMNS)
        self.assertNotIn("target", split.x_train)
        self.assertNotIn("sample_id", split.x_train)

    def test_baseline_ignores_features_and_predicts_training_majority(self) -> None:
        result = evaluate_most_frequent_baseline(split_dataset(self.frame))
        self.assertEqual(result.predicted_label, 0)
        self.assertAlmostEqual(result.accuracy, 2 / 3)
        self.assertEqual(result.recall, 0)

    def test_invalid_schema_missing_duplicate_and_target_are_rejected(self) -> None:
        invalid_frames = (
            self.frame.drop(columns=["noise"]),
            self.frame.assign(signal_a=None),
            pd.concat((self.frame, self.frame.iloc[[0]]), ignore_index=True),
            self.frame.assign(target=2),
        )
        for frame in invalid_frames:
            with self.assertRaises(ValueError):
                validate_dataset(frame)

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("train_rows=90,class_counts=0:60,1:30", report)
        self.assertIn("validation_rows=30,class_counts=0:20,1:10", report)
        self.assertIn("baseline_accuracy=0.667", report)
        self.assertTrue(report.endswith("invariants=target-excluded,stratified-split,validation-untouched"))


if __name__ == "__main__":
    unittest.main()
