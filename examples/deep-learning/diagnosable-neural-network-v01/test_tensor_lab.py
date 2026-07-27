from __future__ import annotations

import unittest

import torch

from tensor_lab import (
    BATCH_SIZE,
    FEATURE_COUNT,
    HIDDEN_WIDTH,
    TensorDataset,
    build_dataset,
    fixed_report,
    linear_projection,
    take_batch,
    validate_dataset,
)


class TensorLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def setUp(self) -> None:
        self.dataset = build_dataset()

    def test_dataset_contract_has_aligned_shapes_and_class_dtypes(self) -> None:
        validate_dataset(self.dataset)
        self.assertEqual(tuple(self.dataset.inputs.shape), (96, FEATURE_COUNT))
        self.assertEqual(tuple(self.dataset.targets.shape), (96,))
        self.assertEqual(self.dataset.inputs.dtype, torch.float32)
        self.assertEqual(self.dataset.targets.dtype, torch.int64)

    def test_generation_repeats_for_same_seed_and_changes_for_new_seed(self) -> None:
        self.assertTrue(torch.equal(build_dataset(7).inputs, build_dataset(7).inputs))
        self.assertFalse(torch.equal(build_dataset(7).inputs, build_dataset(8).inputs))

    def test_dataset_is_balanced_finite_and_keeps_tensors_on_one_device(self) -> None:
        self.assertEqual(torch.bincount(self.dataset.targets, minlength=2).tolist(), [48, 48])
        self.assertTrue(bool(torch.isfinite(self.dataset.inputs).all()))
        self.assertEqual(self.dataset.inputs.device, self.dataset.targets.device)

    def test_batch_preserves_row_alignment_and_feature_width(self) -> None:
        batch = take_batch(self.dataset)
        self.assertEqual(tuple(batch.inputs.shape), (BATCH_SIZE, FEATURE_COUNT))
        self.assertEqual(tuple(batch.targets.shape), (BATCH_SIZE,))
        self.assertTrue(torch.equal(batch.inputs, self.dataset.inputs[:BATCH_SIZE]))
        self.assertTrue(torch.equal(batch.targets, self.dataset.targets[:BATCH_SIZE]))

    def test_matrix_multiplication_and_bias_broadcast_have_explicit_shape(self) -> None:
        projected = linear_projection(take_batch(self.dataset))
        self.assertEqual(tuple(projected.shape), (BATCH_SIZE, HIDDEN_WIDTH))
        self.assertEqual(projected.dtype, torch.float32)

    def test_invalid_shape_and_row_alignment_are_rejected(self) -> None:
        invalid = (
            TensorDataset(self.dataset.inputs[:, :1], self.dataset.targets),
            TensorDataset(self.dataset.inputs, self.dataset.targets[:-1]),
            TensorDataset(self.dataset.inputs.unsqueeze(0), self.dataset.targets),
        )
        for dataset in invalid:
            with self.assertRaises(ValueError):
                validate_dataset(dataset)

    def test_invalid_dtype_device_and_nonfinite_values_are_rejected(self) -> None:
        invalid_dtype = TensorDataset(self.dataset.inputs.to(torch.float64), self.dataset.targets)
        invalid_target = TensorDataset(self.dataset.inputs, self.dataset.targets.to(torch.float32))
        invalid_finite = TensorDataset(self.dataset.inputs.clone(), self.dataset.targets)
        invalid_finite.inputs[0, 0] = float("nan")
        with self.assertRaises(TypeError):
            validate_dataset(invalid_dtype)
        with self.assertRaises(TypeError):
            validate_dataset(invalid_target)
        with self.assertRaises(ValueError):
            validate_dataset(invalid_finite)

    def test_batch_bounds_and_fixed_report_are_deterministic(self) -> None:
        with self.assertRaises(ValueError):
            take_batch(self.dataset, 0)
        with self.assertRaises(ValueError):
            take_batch(self.dataset, 97)
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("rows=96,features=2,classes=0:48,1:48", report)
        self.assertIn("linear_contract=8x2 @ 2x3 + 3 -> 8x3", report)
        self.assertTrue(report.endswith("invariants=feature-rank2,target-rank1,row-aligned,cpu-deterministic"))


if __name__ == "__main__":
    unittest.main()
