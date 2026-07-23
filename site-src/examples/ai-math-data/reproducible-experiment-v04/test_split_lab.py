from __future__ import annotations

import random
import unittest

from split_lab import LabeledSample, fixed_report, stratified_split


class SplitLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.samples = tuple(
            LabeledSample(sample_id, label)
            for sample_id, label in (
                ("a", 0), ("b", 0), ("c", 0), ("d", 0),
                ("e", 1), ("f", 1), ("g", 1), ("h", 1),
            )
        )

    def test_same_seed_produces_same_split(self) -> None:
        first = stratified_split(self.samples, validation_per_label=1, seed=7)
        second = stratified_split(tuple(reversed(self.samples)), validation_per_label=1, seed=7)
        self.assertEqual(first, second)

    def test_split_has_no_overlap_or_loss(self) -> None:
        split = stratified_split(self.samples, validation_per_label=1, seed=7)
        training = {sample.sample_id for sample in split.training}
        validation = {sample.sample_id for sample in split.validation}
        self.assertFalse(training & validation)
        self.assertEqual(training | validation, {sample.sample_id for sample in self.samples})

    def test_each_partition_preserves_both_labels(self) -> None:
        split = stratified_split(self.samples, validation_per_label=1, seed=7)
        self.assertEqual(split.label_counts("training"), ((0, 3), (1, 3)))
        self.assertEqual(split.label_counts("validation"), ((0, 1), (1, 1)))

    def test_local_rng_does_not_change_global_random_state(self) -> None:
        random.seed(99)
        expected = random.random()
        random.seed(99)
        stratified_split(self.samples, validation_per_label=1, seed=7)
        self.assertEqual(random.random(), expected)

    def test_duplicate_invalid_and_too_small_inputs_are_rejected(self) -> None:
        invalid_cases = (
            (self.samples + (LabeledSample("a", 0),), 1),
            ((LabeledSample("a", 0), LabeledSample("b", 2), LabeledSample("c", 1)), 1),
            ((LabeledSample("a", 0), LabeledSample("b", 1)), 1),
            (self.samples, 0),
        )
        for samples, per_label in invalid_cases:
            with self.assertRaises(ValueError):
                stratified_split(samples, validation_per_label=per_label, seed=7)

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("overlap=0", report)
        self.assertIn("repeated=identical", report)
        self.assertIn("validation_label_counts=0:1,1:1", report)
        self.assertTrue(report.endswith("invariants=seeded-local-rng,stratified,no-overlap"))


if __name__ == "__main__":
    unittest.main()
