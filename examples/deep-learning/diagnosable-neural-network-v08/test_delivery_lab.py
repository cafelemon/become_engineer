from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import torch

from delivery_lab import (
    MANIFEST_FILENAME,
    MODEL_FILENAME,
    build_selected_model,
    export_artifact,
    fixed_report,
    load_artifact,
    predict,
    validate_record,
)


class DeliveryLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def test_export_creates_state_dict_and_manifest_without_training_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = export_artifact(root, build_selected_model())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertTrue((root / MODEL_FILENAME).is_file())
            self.assertEqual(manifest["model_file"], MODEL_FILENAME)
            self.assertNotIn("optimizer", manifest)
            self.assertNotIn("rng", manifest)
            self.assertEqual(list(root.glob("*.tmp")), [])

    def test_load_validates_manifest_and_restores_eval_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = export_artifact(Path(directory), build_selected_model())
            model, manifest = load_artifact(manifest_path)
        self.assertFalse(model.training)
        self.assertEqual(manifest["artifact_version"], 1)
        self.assertEqual(manifest["output_schema"]["labels"], ["negative", "positive"])

    def test_prediction_contract_returns_label_and_normalized_probabilities(self) -> None:
        model = build_selected_model()
        negative = predict(model, {"signal_a": -1.0, "signal_b": 0.0})
        positive = predict(model, {"signal_a": 1.0, "signal_b": 0.0})
        self.assertEqual((negative.label, positive.label), ("negative", "positive"))
        self.assertAlmostEqual(sum(negative.probabilities), 1.0, places=6)
        self.assertAlmostEqual(sum(positive.probabilities), 1.0, places=6)

    def test_predict_forces_eval_and_is_deterministic_without_gradients(self) -> None:
        model = build_selected_model()
        model.train()
        record = {"signal_a": 0.8, "signal_b": -0.2}
        first, second = predict(model, record), predict(model, record)
        self.assertEqual(first, second)
        self.assertFalse(model.training)
        self.assertTrue(all(parameter.grad is None for parameter in model.parameters()))

    def test_missing_and_extra_fields_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_record({"signal_a": 1.0})
        with self.assertRaises(ValueError):
            validate_record({"signal_a": 1.0, "signal_b": 0.0, "debug": 1})

    def test_wrong_types_booleans_and_nonfinite_values_are_rejected(self) -> None:
        for record in [
            {"signal_a": "1", "signal_b": 0.0},
            {"signal_a": True, "signal_b": 0.0},
            {"signal_a": float("nan"), "signal_b": 0.0},
            {"signal_a": 0.0, "signal_b": float("inf")},
        ]:
            with self.subTest(record=record):
                with self.assertRaises((TypeError, ValueError)):
                    validate_record(record)

    def test_tampered_model_is_rejected_before_load(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = export_artifact(root, build_selected_model())
            with (root / MODEL_FILENAME).open("ab") as handle:
                handle.write(b"tampered")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_artifact(manifest_path)

    def test_incompatible_schema_and_path_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = export_artifact(root, build_selected_model())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["model_file"] = "../outside.pt"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "model path"):
                load_artifact(root / MANIFEST_FILENAME)

    def test_fixed_report_is_deterministic_and_states_delivery_boundary(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("inference=eval:true,inference_mode:true,requires_grad:false,deterministic:true", report)
        self.assertIn("tampered_model=rejected", report)
        self.assertTrue(report.endswith(
            "invariants=state-dict-only,manifest-validated,trusted-local-artifact,no-network,no-personal-data"
        ))


if __name__ == "__main__":
    unittest.main()
