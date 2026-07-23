from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from unsupervised_lab import (
    NUMERIC_COLUMNS,
    build_dataset,
    build_projection,
    feature_matrix,
    fixed_report,
    run_unsupervised,
)


class UnsupervisedLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = build_dataset()

    def test_feature_matrix_excludes_identifier_and_target(self) -> None:
        values = feature_matrix(self.frame)
        self.assertEqual(tuple(values.columns), NUMERIC_COLUMNS)
        self.assertNotIn("sample_id", values)
        self.assertNotIn("target", values)

    def test_projection_imputes_scales_and_reduces_to_two_components(self) -> None:
        transformed = build_projection().fit_transform(feature_matrix(self.frame))
        self.assertEqual(transformed.shape, (120, 2))
        self.assertFalse(np.isnan(transformed).any())
        np.testing.assert_allclose(transformed.mean(axis=0), 0, atol=1e-12)

    def test_pca_explained_variance_is_bounded_and_ordered(self) -> None:
        result = run_unsupervised(self.frame)
        first, second = result.explained_variance_ratio
        self.assertGreaterEqual(first, second)
        self.assertGreater(first, 0)
        self.assertLessEqual(first + second, 1)

    def test_kmeans_assigns_every_row_to_requested_clusters(self) -> None:
        result = run_unsupervised(self.frame, 2)
        self.assertEqual(len(result.labels), 120)
        self.assertEqual(set(result.labels), {0, 1})
        self.assertEqual(sum(result.cluster_sizes), 120)
        self.assertGreater(result.inertia, 0)

    def test_silhouette_is_bounded_and_candidates_are_explicit(self) -> None:
        scores = [run_unsupervised(self.frame, k).silhouette for k in (2, 3, 4)]
        for score in scores:
            self.assertGreaterEqual(score, -1)
            self.assertLessEqual(score, 1)
        self.assertEqual(len(scores), 3)

    def test_fixed_seed_is_deterministic_up_to_exact_labels(self) -> None:
        first = run_unsupervised(self.frame, 3)
        second = run_unsupervised(self.frame, 3)
        np.testing.assert_array_equal(first.labels, second.labels)
        np.testing.assert_allclose(first.transformed, second.transformed)

    def test_invalid_schema_types_and_cluster_counts_are_rejected(self) -> None:
        invalid_frames = (self.frame.drop(columns=["noise"]), self.frame.assign(signal_a="bad"), self.frame.assign(sample_id="same"))
        for frame in invalid_frames:
            with self.assertRaises(ValueError):
                feature_matrix(frame)
        for clusters in (1, len(self.frame)):
            with self.assertRaises(ValueError):
                run_unsupervised(self.frame, clusters)

    def test_fixed_report_is_deterministic_and_keeps_raw_features(self) -> None:
        before = feature_matrix(self.frame)
        report = fixed_report()
        pd.testing.assert_frame_equal(before, feature_matrix(self.frame))
        self.assertIn("target_used_for_fit=false", report)
        self.assertIn("interpretation=clusters-are-descriptive-not-ground-truth", report)
        self.assertTrue(report.endswith("invariants=no-target-fit,scaled-before-pca,fixed-random-state"))


if __name__ == "__main__":
    unittest.main()
