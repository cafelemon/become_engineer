from __future__ import annotations

import unittest

from decision_tree_lab import (
    FEATURE_COLUMNS,
    build_dataset,
    build_pipeline,
    evaluate,
    fixed_report,
    split_dataset,
    tree_rules,
)


class DecisionTreeLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.split = split_dataset(build_dataset())

    def test_split_preserves_feature_and_validation_boundary(self) -> None:
        self.assertEqual(tuple(self.split.x_train.columns), FEATURE_COLUMNS)
        self.assertEqual((len(self.split.x_train), len(self.split.x_validation)), (90, 30))
        self.assertNotIn("target", self.split.x_train)

    def test_unconstrained_tree_can_fit_training_data_more_tightly(self) -> None:
        model = build_pipeline(None).fit(self.split.x_train, self.split.y_train)
        result = evaluate(model, self.split)
        self.assertEqual(result.train_accuracy, 1)
        self.assertGreater(result.actual_depth, 3)
        self.assertGreater(result.node_count, result.leaf_count)

    def test_constraints_reduce_depth_nodes_and_leaves(self) -> None:
        unconstrained = evaluate(build_pipeline(None).fit(self.split.x_train, self.split.y_train), self.split)
        constrained = evaluate(build_pipeline(3, 5).fit(self.split.x_train, self.split.y_train), self.split)
        self.assertLessEqual(constrained.actual_depth, 3)
        self.assertLess(constrained.node_count, unconstrained.node_count)
        self.assertLess(constrained.leaf_count, unconstrained.leaf_count)

    def test_tree_uses_named_transformed_feature_at_root(self) -> None:
        model = build_pipeline(3, 5).fit(self.split.x_train, self.split.y_train)
        result = evaluate(model, self.split)
        self.assertIn(result.root_feature, model.named_steps["preprocess"].get_feature_names_out())
        self.assertGreater(result.root_threshold, -100)

    def test_exported_rules_include_branches_and_classes(self) -> None:
        model = build_pipeline(3, 5).fit(self.split.x_train, self.split.y_train)
        rules = tree_rules(model)
        self.assertIn("|---", rules)
        self.assertIn("class:", rules)

    def test_fixed_seed_makes_structure_deterministic(self) -> None:
        first = build_pipeline(None).fit(self.split.x_train, self.split.y_train)
        second = build_pipeline(None).fit(self.split.x_train, self.split.y_train)
        self.assertEqual(tree_rules(first), tree_rules(second))

    def test_invalid_complexity_limits_are_rejected(self) -> None:
        for depth, leaf in ((0, 1), (-1, 1), (3, 0)):
            with self.assertRaises(ValueError):
                build_pipeline(depth, leaf)

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("model=decision-tree,criterion=gini", report)
        self.assertIn("capacity_reduced=true", report)
        self.assertIn("training_gap_unconstrained=", report)
        self.assertTrue(report.endswith("invariants=train-only-fit,fixed-seed,validation-for-comparison"))


if __name__ == "__main__":
    unittest.main()
