from __future__ import annotations

import unittest

import torch

from training_lab import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_EPOCHS,
    TRAIN_PER_CLASS,
    VALIDATION_PER_CLASS,
    build_model,
    build_splits,
    epoch_batches,
    evaluate,
    fixed_report,
    train,
)


class TrainingLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def setUp(self) -> None:
        self.splits = build_splits()

    def test_split_is_balanced_and_train_validation_are_distinct(self) -> None:
        self.assertEqual(torch.bincount(self.splits.train.targets).tolist(), [TRAIN_PER_CLASS, TRAIN_PER_CLASS])
        self.assertEqual(torch.bincount(self.splits.validation.targets).tolist(), [VALIDATION_PER_CLASS, VALIDATION_PER_CLASS])
        self.assertEqual(self.splits.train.inputs.shape[0], 72)
        self.assertEqual(self.splits.validation.inputs.shape[0], 24)

    def test_each_epoch_order_covers_every_training_row_once(self) -> None:
        batches = epoch_batches(72, DEFAULT_BATCH_SIZE, 7, 3)
        indexes = torch.cat(batches)
        self.assertEqual(len(indexes), 72)
        self.assertEqual(torch.sort(indexes).values.tolist(), list(range(72)))
        self.assertEqual(len(batches), 6)

    def test_batch_order_is_repeatable_by_seed_and_changes_by_epoch(self) -> None:
        first = torch.cat(epoch_batches(72, DEFAULT_BATCH_SIZE, 7, 1))
        repeated = torch.cat(epoch_batches(72, DEFAULT_BATCH_SIZE, 7, 1))
        next_epoch = torch.cat(epoch_batches(72, DEFAULT_BATCH_SIZE, 7, 2))
        self.assertTrue(torch.equal(first, repeated))
        self.assertFalse(torch.equal(first, next_epoch))

    def test_training_reduces_loss_and_reaches_high_training_accuracy(self) -> None:
        model = build_model()
        initial_loss, _ = evaluate(model, self.splits.train)
        result = train(model, self.splits.train)
        final_loss, final_accuracy = evaluate(model, self.splits.train)
        self.assertLess(final_loss, initial_loss * 0.25)
        self.assertGreaterEqual(final_accuracy, 0.98)
        self.assertGreater(result.parameter_update_norm, 0)

    def test_history_records_every_epoch_step_and_row(self) -> None:
        result = train(build_model(), self.splits.train)
        self.assertEqual(len(result.history), DEFAULT_EPOCHS)
        self.assertEqual(result.steps, DEFAULT_EPOCHS * 6)
        self.assertTrue(all(record.rows_seen == 72 for record in result.history))
        self.assertEqual([record.epoch for record in result.history], list(range(1, DEFAULT_EPOCHS + 1)))

    def test_zero_learning_rate_keeps_parameters_unchanged(self) -> None:
        model = build_model()
        before = tuple(parameter.detach().clone() for parameter in model.parameters())
        result = train(model, self.splits.train, learning_rate=0.0, epochs=2)
        self.assertEqual(result.parameter_update_norm, 0.0)
        self.assertTrue(all(torch.equal(left, right) for left, right in zip(before, model.parameters())))

    def test_invalid_learning_rate_epoch_and_batch_are_rejected(self) -> None:
        for learning_rate in (-0.1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                train(build_model(), self.splits.train, learning_rate=learning_rate)
        with self.assertRaises(ValueError):
            train(build_model(), self.splits.train, epochs=0)
        with self.assertRaises(ValueError):
            train(build_model(), self.splits.train, batch_size=0)

    def test_fixed_report_is_deterministic_and_keeps_validation_untouched(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("history=epochs:30,steps:180,rows_per_epoch:72", report)
        self.assertIn("learning_rate_zero=no_parameter_change:true", report)
        self.assertIn("validation_untouched=true", report)
        self.assertTrue(report.endswith("invariants=zero-backward-step,all-train-batches-once,history-recorded,validation-untouched"))


if __name__ == "__main__":
    unittest.main()
