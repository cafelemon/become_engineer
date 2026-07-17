from __future__ import annotations

import unittest

from experiment import generate_rows, run_experiment


class ExperimentTest(unittest.TestCase):
    def test_generator_is_repeatable(self) -> None:
        self.assertEqual(generate_rows(), generate_rows())
        self.assertEqual(len(generate_rows()), 240)

    def test_dataset_contains_both_labels(self) -> None:
        labels = {row["goal_met"] for row in generate_rows()}
        self.assertEqual(labels, {0, 1})

    def test_model_beats_the_simple_baseline(self) -> None:
        result = run_experiment(generate_rows())
        self.assertGreater(result.model_accuracy, result.baseline_accuracy)
        self.assertEqual(sum(sum(row) for row in result.matrix), 60)
        self.assertEqual(result.mistakes, 60 - sum(result.matrix[index][index] for index in range(2)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
