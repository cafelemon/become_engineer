from __future__ import annotations

import unittest

from sklearn.model_selection import StratifiedKFold

from model_selection_lab import (
    FEATURE_COLUMNS,
    build_dataset,
    build_search,
    fixed_report,
    make_holdout,
    run_selection,
)


class ModelSelectionLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.split = make_holdout(build_dataset())

    def test_holdout_is_stratified_disjoint_and_complete(self) -> None:
        self.assertEqual((len(self.split.x_development), len(self.split.x_test)), (90, 30))
        self.assertFalse(set(self.split.development_ids) & set(self.split.test_ids))
        self.assertEqual(len(set(self.split.development_ids) | set(self.split.test_ids)), 120)
        self.assertEqual(tuple(self.split.x_development.columns), FEATURE_COLUMNS)
        self.assertEqual(self.split.y_test.value_counts().sort_index().to_dict(), {0: 20, 1: 10})

    def test_search_uses_stratified_shuffled_five_fold_cv(self) -> None:
        search = build_search()
        self.assertIsInstance(search.cv, StratifiedKFold)
        self.assertEqual(search.cv.n_splits, 5)
        self.assertTrue(search.cv.shuffle)
        self.assertEqual(search.scoring, "balanced_accuracy")

    def test_preprocessing_is_inside_the_estimator_given_to_cv(self) -> None:
        search = build_search()
        self.assertEqual(tuple(search.estimator.named_steps), ("preprocess", "classifier"))
        branch_names = [name for name, _, _ in search.estimator.named_steps["preprocess"].transformers]
        self.assertEqual(branch_names, ["numeric", "categorical"])

    def test_grid_has_six_explicit_candidates(self) -> None:
        search = build_search()
        self.assertEqual(search.param_grid[0]["classifier__C"], [0.1, 1.0, 10.0])
        self.assertEqual(search.param_grid[1]["classifier__max_depth"], [2, 3, 4])

    def test_selection_refits_best_pipeline_on_development_set(self) -> None:
        result = run_selection(self.split)
        self.assertTrue(result.search.refit)
        self.assertEqual(result.search.n_splits_, 5)
        self.assertEqual(len(result.search.cv_results_["params"]), 6)
        self.assertIn(result.best_family, {"logistic-regression", "decision-tree"})

    def test_final_test_metrics_are_bounded_and_not_cv_score_aliases(self) -> None:
        result = run_selection(self.split)
        for value in (result.test_accuracy, result.test_balanced_accuracy, result.test_recall):
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)
        self.assertNotEqual(id(result.search.cv_results_), id(self.split.y_test))

    def test_holdout_rejects_schema_drift_and_duplicate_ids(self) -> None:
        frame = build_dataset()
        invalid = (frame.drop(columns=["noise"]), frame.assign(sample_id="same"))
        for candidate in invalid:
            with self.assertRaises(ValueError):
                make_holdout(candidate)

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("candidate_count=6,fit_count=30", report)
        self.assertIn("test_access=after-selection-once", report)
        self.assertIn("selected=", report)
        self.assertTrue(report.endswith("invariants=preprocess-inside-cv,test-excluded-from-selection,refit-development-only"))


if __name__ == "__main__":
    unittest.main()
