from __future__ import annotations

import unittest

import numpy as np

from logistic_regression_lab import (
    FEATURE_COLUMNS,
    build_dataset,
    build_pipeline,
    evaluate,
    fit_and_evaluate,
    fixed_report,
    split_dataset,
)


class LogisticRegressionLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.split = split_dataset(build_dataset())

    def test_split_keeps_v02_feature_and_validation_contract(self) -> None:
        self.assertEqual(tuple(self.split.x_train.columns), FEATURE_COLUMNS)
        self.assertEqual((len(self.split.x_train), len(self.split.x_validation)), (90, 30))
        self.assertNotIn("target", self.split.x_train)
        self.assertNotIn("sample_id", self.split.x_train)

    def test_pipeline_contains_preprocessing_and_logistic_classifier(self) -> None:
        pipeline = build_pipeline()
        self.assertEqual(tuple(pipeline.named_steps), ("preprocess", "classifier"))
        self.assertEqual(pipeline.named_steps["classifier"].l1_ratio, 0)
        self.assertEqual(pipeline.named_steps["classifier"].solver, "lbfgs")

    def test_fit_produces_binary_probabilities_and_named_coefficients(self) -> None:
        pipeline = build_pipeline().fit(self.split.x_train, self.split.y_train)
        probabilities = pipeline.predict_proba(self.split.x_validation)
        names = pipeline.named_steps["preprocess"].get_feature_names_out()
        self.assertEqual(probabilities.shape, (30, 2))
        np.testing.assert_allclose(probabilities.sum(axis=1), 1)
        self.assertEqual(pipeline.named_steps["classifier"].coef_.shape, (1, len(names)))

    def test_threshold_half_matches_pipeline_prediction(self) -> None:
        pipeline = build_pipeline().fit(self.split.x_train, self.split.y_train)
        positive = pipeline.predict_proba(self.split.x_validation)[:, 1]
        np.testing.assert_array_equal((positive >= 0.5).astype(int), pipeline.predict(self.split.x_validation))

    def test_log_loss_uses_probabilities_and_model_improves_positive_recall(self) -> None:
        pipeline, result = fit_and_evaluate()
        self.assertGreaterEqual(result.accuracy, 2 / 3)
        self.assertGreater(result.recall, 0)
        self.assertGreater(result.loss, 0)
        self.assertLess(result.loss, 0.637)
        self.assertIsNotNone(pipeline)

    def test_stronger_l2_regularization_reduces_coefficient_norm(self) -> None:
        strong = build_pipeline(0.1).fit(self.split.x_train, self.split.y_train)
        weak = build_pipeline(10).fit(self.split.x_train, self.split.y_train)
        self.assertLess(evaluate(strong, self.split).coefficient_l2, evaluate(weak, self.split).coefficient_l2)

    def test_invalid_regularization_strength_is_rejected(self) -> None:
        for c in (0, -1):
            with self.assertRaises(ValueError):
                build_pipeline(c)

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("model=logistic-regression,penalty=l2", report)
        self.assertIn("validation_accuracy=", report)
        self.assertIn("weaker_regularization_larger_norm=true", report)
        self.assertTrue(report.endswith("invariants=train-only-preprocessing,probabilities-not-decisions,validation-not-fit"))


if __name__ == "__main__":
    unittest.main()
