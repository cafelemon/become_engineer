from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from preprocessing_lab import (
    CATEGORICAL_COLUMNS,
    EXPECTED_COLUMNS,
    FEATURE_COLUMNS,
    NUMERIC_COLUMNS,
    build_dataset,
    build_pipeline,
    fixed_report,
    split_dataset,
    transformed_feature_names,
    validate_dataset,
)


class PreprocessingLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = build_dataset()
        self.split = split_dataset(self.frame)

    def test_dataset_contract_allows_controlled_missing_values(self) -> None:
        validate_dataset(self.frame)
        self.assertEqual(tuple(self.frame.columns), EXPECTED_COLUMNS)
        self.assertEqual(tuple(self.split.x_train.columns), FEATURE_COLUMNS)
        self.assertGreater(self.frame[list(FEATURE_COLUMNS)].isna().sum().sum(), 0)

    def test_schema_rejects_wrong_types_all_missing_and_invalid_target(self) -> None:
        invalid_frames = (
            self.frame.assign(signal_a="not-numeric"),
            self.frame.assign(channel=pd.NA),
            self.frame.drop(columns=["noise"]),
            self.frame.assign(target=2),
        )
        for frame in invalid_frames:
            with self.assertRaises(ValueError):
                validate_dataset(frame)

    def test_column_transformer_has_separate_numeric_and_categorical_paths(self) -> None:
        pipeline = build_pipeline().fit(self.split.x_train, self.split.y_train)
        preprocessor = pipeline.named_steps["preprocess"]
        self.assertEqual(tuple(preprocessor.transformers_[0][2]), NUMERIC_COLUMNS)
        self.assertEqual(tuple(preprocessor.transformers_[1][2]), CATEGORICAL_COLUMNS)
        self.assertIn("numeric__signal_a", transformed_feature_names(pipeline))
        self.assertTrue(any(name.startswith("categorical__channel_") for name in transformed_feature_names(pipeline)))

    def test_fit_statistics_come_only_from_training_rows(self) -> None:
        pipeline = build_pipeline().fit(self.split.x_train, self.split.y_train)
        imputer = pipeline.named_steps["preprocess"].named_transformers_["numeric"].named_steps["imputer"]
        expected = self.split.x_train.loc[:, NUMERIC_COLUMNS].median().to_numpy()
        np.testing.assert_allclose(imputer.statistics_, expected)
        altered_validation = self.split.x_validation.copy()
        altered_validation["signal_a"] = 1_000_000
        pipeline.predict(altered_validation)
        np.testing.assert_allclose(imputer.statistics_, expected)

    def test_transform_removes_missing_values_without_mutating_raw_validation(self) -> None:
        raw_validation = self.split.x_validation.copy(deep=True)
        pipeline = build_pipeline().fit(self.split.x_train, self.split.y_train)
        transformed = pipeline.named_steps["preprocess"].transform(self.split.x_validation)
        self.assertFalse(np.isnan(transformed).any())
        pd.testing.assert_frame_equal(self.split.x_validation, raw_validation)

    def test_unknown_category_is_ignored_by_the_fitted_pipeline(self) -> None:
        pipeline = build_pipeline().fit(self.split.x_train, self.split.y_train)
        inference = self.split.x_validation.iloc[[0]].copy()
        inference.loc[:, "channel"] = "partner"
        transformed = pipeline.named_steps["preprocess"].transform(inference)
        categorical_width = len(transformed_feature_names(pipeline)) - len(NUMERIC_COLUMNS)
        self.assertEqual(transformed.shape[1], len(NUMERIC_COLUMNS) + categorical_width)
        self.assertEqual(transformed[0, -categorical_width:].sum(), 0)
        self.assertEqual(pipeline.predict(inference).shape, (1,))

    def test_target_and_identifier_never_enter_the_preprocessor(self) -> None:
        pipeline = build_pipeline().fit(self.split.x_train, self.split.y_train)
        names = transformed_feature_names(pipeline)
        self.assertFalse(any("target" in name or "sample_id" in name for name in names))

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("fit_scope=train-only", report)
        self.assertIn("post_transform_missing=0", report)
        self.assertIn("unknown_category=ignored,raw_validation_unchanged=true", report)
        self.assertTrue(report.endswith("invariants=target-excluded,fit-train-only,same-pipeline-for-validation"))


if __name__ == "__main__":
    unittest.main()
