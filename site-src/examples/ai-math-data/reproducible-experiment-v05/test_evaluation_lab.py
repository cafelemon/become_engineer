from __future__ import annotations

import unittest

from evaluation_lab import Confusion, ScoredSample, confusion_at_threshold, fixed_report, negative_baseline


class EvaluationLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.samples = (
            ScoredSample("a", 1, 0.9), ScoredSample("b", 1, 0.6),
            ScoredSample("c", 1, 0.4), ScoredSample("d", 0, 0.8),
            ScoredSample("e", 0, 0.3), ScoredSample("f", 0, 0.1),
        )

    def test_threshold_includes_scores_equal_to_boundary(self) -> None:
        samples = (ScoredSample("a", 1, 0.5), ScoredSample("b", 0, 0.4))
        self.assertEqual(confusion_at_threshold(samples, 0.5), Confusion(1, 0, 1, 0))

    def test_confusion_counts_cover_each_sample_once(self) -> None:
        confusion = confusion_at_threshold(self.samples, 0.5)
        self.assertEqual(confusion, Confusion(2, 1, 2, 1))
        self.assertEqual(confusion.total, len(self.samples))

    def test_metrics_are_derived_from_confusion_counts(self) -> None:
        confusion = confusion_at_threshold(self.samples, 0.5)
        self.assertAlmostEqual(confusion.accuracy(), 4 / 6)
        self.assertAlmostEqual(confusion.precision(), 2 / 3)
        self.assertAlmostEqual(confusion.recall(), 2 / 3)
        self.assertAlmostEqual(confusion.f1(), 2 / 3)

    def test_zero_denominators_have_declared_zero_result(self) -> None:
        confusion = Confusion(0, 0, 3, 2)
        self.assertEqual(confusion.precision(), 0)
        self.assertEqual(confusion.recall(), 0)
        self.assertEqual(confusion.f1(), 0)

    def test_baseline_and_invalid_inputs(self) -> None:
        self.assertEqual(negative_baseline(self.samples), Confusion(0, 0, 3, 3))
        for call in (
            lambda: confusion_at_threshold((), 0.5),
            lambda: confusion_at_threshold(self.samples, 1.1),
            lambda: confusion_at_threshold(self.samples + (ScoredSample("a", 0, 0.2),), 0.5),
            lambda: confusion_at_threshold((ScoredSample("x", 2, 0.2),), 0.5),
        ):
            with self.assertRaises(ValueError):
                call()

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("threshold_0.5=tp:2,fp:1,tn:2,fn:1", report)
        self.assertIn("threshold_0.7=tp:1,fp:1,tn:2,fn:2", report)
        self.assertTrue(report.endswith("invariants=fixed-validation,threshold-declared,zero-division-defined"))


if __name__ == "__main__":
    unittest.main()
