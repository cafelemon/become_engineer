from __future__ import annotations

import unittest

import torch
from torch import nn

from forward_lab import (
    BATCH_SIZE,
    CLASS_COUNT,
    FEATURE_COUNT,
    HIDDEN_WIDTH,
    TinyClassifier,
    build_dataset,
    build_model,
    count_trainable_parameters,
    fixed_report,
    take_batch,
)


class ForwardLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def setUp(self) -> None:
        self.batch = take_batch(build_dataset())
        self.model = build_model()

    def test_module_registers_two_linear_layers_and_relu(self) -> None:
        self.assertIsInstance(self.model, nn.Module)
        self.assertIsInstance(self.model.fc1, nn.Linear)
        self.assertIsInstance(self.model.activation, nn.ReLU)
        self.assertIsInstance(self.model.fc2, nn.Linear)

    def test_parameter_names_shapes_and_count_are_explicit(self) -> None:
        shapes = {name: tuple(parameter.shape) for name, parameter in self.model.named_parameters()}
        self.assertEqual(shapes, {
            "fc1.weight": (HIDDEN_WIDTH, FEATURE_COUNT),
            "fc1.bias": (HIDDEN_WIDTH,),
            "fc2.weight": (CLASS_COUNT, HIDDEN_WIDTH),
            "fc2.bias": (CLASS_COUNT,),
        })
        self.assertEqual(count_trainable_parameters(self.model), 22)

    def test_forward_trace_preserves_batch_and_changes_feature_widths(self) -> None:
        trace = self.model.trace(self.batch.inputs)
        self.assertEqual(tuple(trace.hidden_linear.shape), (BATCH_SIZE, HIDDEN_WIDTH))
        self.assertEqual(tuple(trace.hidden_active.shape), (BATCH_SIZE, HIDDEN_WIDTH))
        self.assertEqual(tuple(trace.logits.shape), (BATCH_SIZE, CLASS_COUNT))

    def test_relu_removes_negative_hidden_values_without_changing_shape(self) -> None:
        trace = self.model.trace(self.batch.inputs)
        self.assertTrue(bool((trace.hidden_active >= 0).all()))
        self.assertEqual(trace.hidden_linear.shape, trace.hidden_active.shape)
        self.assertTrue(bool((trace.hidden_linear < 0).any()))

    def test_module_call_matches_explicit_trace_and_builds_gradient_graph(self) -> None:
        logits = self.model(self.batch.inputs)
        trace = self.model.trace(self.batch.inputs)
        self.assertTrue(torch.equal(logits, trace.logits))
        self.assertTrue(logits.requires_grad)
        self.assertIsNotNone(logits.grad_fn)

    def test_softmax_converts_logits_to_rowwise_probabilities(self) -> None:
        logits = self.model(self.batch.inputs)
        probabilities = torch.softmax(logits, dim=1)
        self.assertTrue(bool((probabilities >= 0).all()))
        self.assertTrue(bool((probabilities <= 1).all()))
        self.assertTrue(torch.allclose(probabilities.sum(dim=1), torch.ones(BATCH_SIZE)))

    def test_initialization_repeats_for_same_seed_and_rejects_bad_inputs(self) -> None:
        first, second, different = build_model(7), build_model(7), build_model(8)
        self.assertTrue(all(torch.equal(left, right) for left, right in zip(first.parameters(), second.parameters())))
        self.assertFalse(all(torch.equal(left, right) for left, right in zip(first.parameters(), different.parameters())))
        with self.assertRaises(ValueError):
            self.model(torch.zeros((BATCH_SIZE, FEATURE_COUNT + 1), dtype=torch.float32))
        with self.assertRaises(TypeError):
            self.model(self.batch.inputs.to(torch.float64))

    def test_fixed_report_is_deterministic_and_does_not_claim_training(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("forward=8x2->8x4->8x4->8x2", report)
        self.assertIn("parameters=trainable:22,tensors:4", report)
        self.assertIn("probability_rows_sum_one=true", report)
        self.assertTrue(report.endswith("invariants=module-registered,parameter-shapes-explicit,forward-batch-preserved,no-training-yet"))


if __name__ == "__main__":
    unittest.main()
