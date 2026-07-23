from __future__ import annotations

import unittest

import torch

from diagnostics_lab import (
    CLIP_THRESHOLD,
    EXPLOSIVE_LOSS_SCALE,
    build_batch,
    build_model,
    clip_explosive_gradients,
    diagnose,
    fixed_report,
    zero_initialization_stalls_hidden_gradients,
)


class DiagnosticsLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def setUp(self) -> None:
        self.batch = build_batch()

    def test_initialization_is_reproducible_and_scale_sensitive(self) -> None:
        first, second, larger = build_model(0.35, 7), build_model(0.35, 7), build_model(0.7, 7)
        self.assertTrue(all(torch.equal(left, right) for left, right in zip(first.parameters(), second.parameters())))
        self.assertFalse(all(torch.equal(left, right) for left, right in zip(first.parameters(), larger.parameters())))

    def test_forward_trace_records_finite_activation_rates_and_magnitudes(self) -> None:
        snapshot = diagnose(build_model(), self.batch)
        self.assertTrue(0 < snapshot.activation_nonzero_1 < 1)
        self.assertTrue(0 < snapshot.activation_nonzero_2 < 1)
        self.assertGreater(snapshot.activation_max, 0)
        self.assertTrue(torch.isfinite(torch.tensor(snapshot.activation_max)))

    def test_every_parameter_has_a_finite_layer_gradient_norm(self) -> None:
        snapshot = diagnose(build_model(), self.batch)
        self.assertEqual(len(snapshot.gradient_norms), 6)
        self.assertTrue(all(value >= 0 and torch.isfinite(torch.tensor(value)) for _, value in snapshot.gradient_norms))
        self.assertGreater(snapshot.global_gradient_norm, 0)

    def test_loss_scaling_scales_global_gradient_norm(self) -> None:
        normal = diagnose(build_model(), self.batch)
        scaled = diagnose(build_model(), self.batch, loss_scale=EXPLOSIVE_LOSS_SCALE)
        self.assertAlmostEqual(
            scaled.global_gradient_norm / normal.global_gradient_norm,
            EXPLOSIVE_LOSS_SCALE,
            places=3,
        )

    def test_gradient_clipping_limits_norm_after_backward_before_step(self) -> None:
        model = build_model()
        before_parameters = tuple(parameter.detach().clone() for parameter in model.parameters())
        before, after = clip_explosive_gradients(model, self.batch)
        self.assertGreater(before, CLIP_THRESHOLD)
        self.assertLessEqual(after, CLIP_THRESHOLD + 1e-5)
        self.assertTrue(all(torch.equal(left, right) for left, right in zip(before_parameters, model.parameters())))

    def test_zero_initialization_stalls_hidden_weight_gradients(self) -> None:
        self.assertTrue(zero_initialization_stalls_hidden_gradients(self.batch))

    def test_nonfinite_input_and_invalid_diagnostic_settings_are_rejected(self) -> None:
        invalid = build_batch()
        invalid.inputs[0, 0] = float("nan")
        with self.assertRaises(ValueError):
            diagnose(build_model(), invalid)
        with self.assertRaises(ValueError):
            diagnose(build_model(), self.batch, loss_scale=0)
        with self.assertRaises(ValueError):
            clip_explosive_gradients(build_model(), self.batch, threshold=0)
        with self.assertRaises(ValueError):
            build_model(scale=float("inf"))

    def test_fixed_report_is_deterministic_and_preserves_root_cause_boundary(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("zero_initialization=hidden_gradients_stalled:true", report)
        self.assertIn("nonfinite_input=rejected", report)
        self.assertTrue(report.endswith("invariants=activations-observed,layer-gradients-finite,clip-after-backward-before-step,root-cause-still-required"))


if __name__ == "__main__":
    unittest.main()
