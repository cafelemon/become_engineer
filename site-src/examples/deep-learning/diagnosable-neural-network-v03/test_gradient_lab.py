from __future__ import annotations

import unittest

import torch

from gradient_lab import (
    CLASS_COUNT,
    TensorBatch,
    accumulation_ratio,
    backward_once,
    build_batch,
    build_model,
    finite_difference_check,
    fixed_report,
    global_gradient_norm,
    loss_for,
)


class GradientLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def setUp(self) -> None:
        self.batch = build_batch()
        self.model = build_model()

    def test_cross_entropy_accepts_logits_and_integer_class_targets(self) -> None:
        loss = loss_for(self.model, self.batch)
        self.assertEqual(loss.ndim, 0)
        self.assertTrue(loss.requires_grad)
        self.assertTrue(bool(torch.isfinite(loss)))

    def test_backward_populates_finite_gradients_for_all_parameters(self) -> None:
        backward_once(self.model, self.batch)
        gradients = [parameter.grad for parameter in self.model.parameters()]
        self.assertEqual(len(gradients), 4)
        self.assertTrue(all(gradient is not None for gradient in gradients))
        self.assertTrue(all(bool(torch.isfinite(gradient).all()) for gradient in gradients if gradient is not None))

    def test_gradient_shapes_match_parameter_shapes_and_norm_is_positive(self) -> None:
        backward_once(self.model, self.batch)
        for parameter in self.model.parameters():
            self.assertEqual(parameter.grad.shape, parameter.shape)
        self.assertGreater(global_gradient_norm(self.model), 0)

    def test_finite_difference_matches_autograd_for_one_parameter(self) -> None:
        check = finite_difference_check(self.model, self.batch)
        self.assertEqual(check.parameter, "fc2.weight[0,1]")
        self.assertGreater(abs(check.autograd), 0.1)
        self.assertLess(check.absolute_error, 1e-4)

    def test_backward_accumulates_until_gradients_are_cleared(self) -> None:
        self.assertAlmostEqual(accumulation_ratio(self.model, self.batch), 2.0, places=5)

    def test_zero_grad_set_to_none_removes_previous_gradient_buffers(self) -> None:
        backward_once(self.model, self.batch)
        self.assertTrue(all(parameter.grad is not None for parameter in self.model.parameters()))
        self.model.zero_grad(set_to_none=True)
        self.assertTrue(all(parameter.grad is None for parameter in self.model.parameters()))

    def test_invalid_target_shape_dtype_and_class_are_rejected(self) -> None:
        invalid_batches = (
            TensorBatch(self.batch.inputs, self.batch.targets.unsqueeze(1)),
            TensorBatch(self.batch.inputs, self.batch.targets.to(torch.float32)),
            TensorBatch(self.batch.inputs, torch.full_like(self.batch.targets, CLASS_COUNT)),
        )
        expected = (ValueError, TypeError, ValueError)
        for batch, error in zip(invalid_batches, expected):
            with self.assertRaises(error):
                loss_for(self.model, batch)

    def test_fixed_report_is_deterministic_and_records_gradient_contract(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("backward=parameter_gradients:4,finite:true", report)
        self.assertIn("accumulation=second_backward:2.000x", report)
        self.assertIn("zero_grad=set_to_none:true", report)
        self.assertTrue(report.endswith("invariants=loss-from-logits,backward-once-per-graph,gradients-checked,zero-before-next-step"))


if __name__ == "__main__":
    unittest.main()
