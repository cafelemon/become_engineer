from __future__ import annotations

import unittest

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold

from calibration_error_lab import (
    THRESHOLD,
    build_dataset,
    build_pipeline,
    expected_calibration_error,
    fixed_report,
    group_error_table,
    make_holdout,
    probability_metrics,
)


class CalibrationErrorLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.split = make_holdout(build_dataset())

    def test_holdout_remains_thirty_rows_with_expected_classes(self) -> None:
        self.assertEqual((len(self.split.x_development), len(self.split.x_test)), (90, 30))
        self.assertEqual(self.split.y_test.value_counts().sort_index().to_dict(), {0: 20, 1: 10})
        self.assertEqual(self.split.test_ids.nunique(), 30)

    def test_calibrator_fits_pipeline_only_on_development_data(self) -> None:
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=20260723)
        model = CalibratedClassifierCV(estimator=build_pipeline(), method="sigmoid", cv=folds)
        model.fit(self.split.x_development, self.split.y_development)
        self.assertEqual(len(model.calibrated_classifiers_), 5)
        self.assertEqual(model.predict_proba(self.split.x_test).shape, (30, 2))

    def test_ece_is_zero_for_perfect_probabilities(self) -> None:
        truth = np.array([0, 0, 1, 1])
        probabilities = np.array([0.0, 0.0, 1.0, 1.0])
        self.assertEqual(expected_calibration_error(truth, probabilities), 0)

    def test_probability_metrics_are_bounded_and_finite(self) -> None:
        model = build_pipeline().fit(self.split.x_development, self.split.y_development)
        probabilities = model.predict_proba(self.split.x_test)[:, 1]
        metrics = probability_metrics(self.split.y_test, probabilities)
        self.assertGreaterEqual(metrics.brier, 0)
        self.assertLessEqual(metrics.brier, 1)
        self.assertGreater(metrics.log_loss, 0)
        self.assertGreaterEqual(metrics.expected_calibration_error, 0)

    def test_group_table_accounts_for_every_test_row(self) -> None:
        model = build_pipeline().fit(self.split.x_development, self.split.y_development)
        probabilities = model.predict_proba(self.split.x_test)[:, 1]
        rows = group_error_table(self.split.x_test, self.split.y_test, probabilities)
        self.assertEqual(sum(row.samples for row in rows), 30)
        self.assertEqual({row.group for row in rows}, {"direct", "missing", "organic", "referral"})
        for row in rows:
            if row.recall is not None:
                self.assertGreaterEqual(row.recall, 0)
                self.assertLessEqual(row.recall, 1)

    def test_threshold_is_predeclared_and_changes_decisions_not_probabilities(self) -> None:
        model = build_pipeline().fit(self.split.x_development, self.split.y_development)
        probabilities = model.predict_proba(self.split.x_test)[:, 1]
        low = probabilities >= THRESHOLD
        high = probabilities >= 0.7
        self.assertGreaterEqual(low.sum(), high.sum())
        np.testing.assert_array_equal(probabilities, model.predict_proba(self.split.x_test)[:, 1])

    def test_invalid_ece_and_threshold_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            expected_calibration_error(np.array([0]), np.array([1.2]))
        with self.assertRaises(ValueError):
            expected_calibration_error(np.array([0, 1]), np.array([0.5]))
        with self.assertRaises(ValueError):
            group_error_table(self.split.x_test, self.split.y_test, np.zeros(30), 1.0)

    def test_fixed_report_is_deterministic_and_discloses_small_groups(self) -> None:
        report = fixed_report()
        self.assertIn("calibration=sigmoid,cv=stratified-5-fold", report)
        self.assertIn("small_groups_descriptive_only=true", report)
        self.assertIn("comparison=report-all-metrics-no-cherry-picking", report)
        self.assertTrue(report.endswith("invariants=calibration-development-only,threshold-predeclared,test-not-retuned"))


if __name__ == "__main__":
    unittest.main()
