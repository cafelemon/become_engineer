from __future__ import annotations

import unittest

import torch

from validation_lab import (
    CandidateConfig,
    NOISY_TRAIN_LABELS,
    TRAIN_ROWS,
    VALIDATION_ROWS,
    build_model,
    build_splits,
    dropout_mode_probe,
    evaluate,
    fixed_report,
    select_candidate,
    train_candidate,
)


class ValidationLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def setUp(self) -> None:
        self.splits = build_splits()
        self.unregularized = CandidateConfig("unregularized", 0.0, 0.0)
        self.regularized = CandidateConfig("regularized", 0.02, 0.25)

    def test_training_labels_have_controlled_noise_and_validation_stays_clean(self) -> None:
        changed = self.splits.train.targets != self.splits.clean_train_targets
        self.assertEqual(int(changed.sum()), NOISY_TRAIN_LABELS)
        self.assertTrue(torch.equal(torch.where(changed)[0], torch.sort(self.splits.noisy_indexes).values))
        self.assertEqual(self.splits.train.inputs.shape[0], TRAIN_ROWS)
        self.assertEqual(self.splits.validation.inputs.shape[0], VALIDATION_ROWS)

    def test_candidates_share_data_initialization_and_budget(self) -> None:
        first = build_model(self.unregularized.dropout)
        second = build_model(self.regularized.dropout)
        for left, right in zip(first.parameters(), second.parameters()):
            self.assertTrue(torch.equal(left, right))
        self.assertTrue(torch.equal(build_splits().train.inputs, self.splits.train.inputs))

    def test_evaluation_disables_gradients_and_leaves_parameter_grads_untouched(self) -> None:
        model = build_model(0.25)
        self.assertTrue(all(parameter.grad is None for parameter in model.parameters()))
        loss, accuracy = evaluate(model, self.splits.validation)
        self.assertTrue(0 <= accuracy <= 1)
        self.assertGreater(loss, 0)
        self.assertTrue(all(parameter.grad is None for parameter in model.parameters()))

    def test_dropout_is_stochastic_in_train_and_stable_in_eval(self) -> None:
        stochastic_train, stable_eval = dropout_mode_probe()
        self.assertTrue(stochastic_train)
        self.assertTrue(stable_eval)

    def test_regularized_candidate_improves_fixed_budget_validation_loss(self) -> None:
        plain = train_candidate(self.unregularized, self.splits)
        regularized = train_candidate(self.regularized, self.splits)
        self.assertLess(regularized.final_validation_loss, plain.final_validation_loss)
        self.assertGreaterEqual(regularized.final_validation_accuracy, plain.final_validation_accuracy)
        self.assertLess(plain.best_validation_loss, regularized.best_validation_loss)

    def test_selection_uses_validation_loss_and_retains_best_state(self) -> None:
        results = (
            train_candidate(self.unregularized, self.splits),
            train_candidate(self.regularized, self.splits),
        )
        selected = select_candidate(results)
        self.assertEqual(selected.config.name, "regularized")
        self.assertGreater(selected.best_epoch, 0)
        self.assertTrue(selected.best_state)
        self.assertTrue(all(isinstance(value, torch.Tensor) for value in selected.best_state.values()))

    def test_invalid_candidate_hyperparameters_and_empty_selection_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_model(1.0)
        with self.assertRaises(ValueError):
            train_candidate(CandidateConfig("bad", -0.1, 0.0), self.splits)
        with self.assertRaises(ValueError):
            train_candidate(self.regularized, self.splits, epochs=0)
        with self.assertRaises(ValueError):
            select_candidate(())

    def test_fixed_report_is_deterministic_and_declares_test_untouched(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("selected=regularized,rule=lowest-final-validation-loss", report)
        self.assertIn("dropout=train_stochastic:true,eval_stable:true", report)
        self.assertIn("test_set=not-used", report)
        self.assertTrue(report.endswith("invariants=same-data-initialization-budget,validation-only-selection,best-state-retained,test-untouched"))


if __name__ == "__main__":
    unittest.main()
