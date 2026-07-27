from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from delivery_lab import (
    FEATURE_COLUMNS,
    FORMAT_VERSION,
    build_dataset,
    fixed_report,
    load_artifact,
    predict_record,
    save_artifact,
    train_delivery_model,
    validate_record,
)


class DeliveryLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = build_dataset()
        self.model = train_delivery_model(self.frame)
        self.sample = {
            "signal_a": 1.2,
            "signal_b": 0.4,
            "noise": -0.1,
            "redundant_signal": 0.6,
            "channel": "direct",
        }

    def test_delivery_model_contains_all_five_calibrated_folds(self) -> None:
        self.assertEqual(len(self.model.calibrated_classifiers_), 5)
        self.assertEqual(self.model.predict_proba(pd.DataFrame([self.sample])).shape, (1, 2))

    def test_manifest_records_schema_versions_threshold_and_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = save_artifact(Path(temporary), self.model, len(self.frame))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["format_version"], FORMAT_VERSION)
            self.assertEqual(manifest["training_rows"], 120)
            self.assertEqual(len(manifest["sha256"]), 64)
            self.assertEqual(manifest["feature_schema"]["additional_properties"], False)
            self.assertEqual(set(manifest["dependencies"]), {"numpy", "pandas", "scikit_learn"})

    def test_loaded_full_pipeline_matches_in_memory_probability_exactly(self) -> None:
        expected = float(self.model.predict_proba(pd.DataFrame([self.sample]))[0, 1])
        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = save_artifact(Path(temporary), self.model, len(self.frame))
            actual = predict_record(load_artifact(manifest_path), self.sample)
        self.assertEqual(actual["positive_probability"], expected)

    def test_schema_accepts_nullable_features_and_unknown_category(self) -> None:
        record = dict(self.sample, signal_a=None, channel="partner")
        validate_record(record)
        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = save_artifact(Path(temporary), self.model, len(self.frame))
            result = predict_record(load_artifact(manifest_path), record)
        self.assertGreaterEqual(result["positive_probability"], 0)
        self.assertLessEqual(result["positive_probability"], 1)

    def test_schema_rejects_missing_extra_nonfinite_and_wrong_types(self) -> None:
        invalid = (
            {key: value for key, value in self.sample.items() if key != "noise"},
            dict(self.sample, extra=1),
            dict(self.sample, signal_a=np.inf),
            dict(self.sample, signal_b=True),
            dict(self.sample, channel=3),
        )
        for record in invalid:
            with self.assertRaises(ValueError):
                validate_record(record)

    def test_checksum_rejects_tampered_model_before_unpickling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = save_artifact(Path(temporary), self.model, len(self.frame))
            model_path = Path(temporary) / "model.pkl"
            model_path.write_bytes(model_path.read_bytes() + b"tampered")
            with self.assertRaisesRegex(ValueError, "checksum-mismatch"):
                load_artifact(manifest_path)

    def test_manifest_rejects_dependency_and_format_drift(self) -> None:
        for field, value, message in (
            ("format_version", 999, "unsupported-format-version"),
            ("dependencies", {}, "dependency-version-mismatch"),
        ):
            with tempfile.TemporaryDirectory() as temporary:
                manifest_path = save_artifact(Path(temporary), self.model, len(self.frame))
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest[field] = value
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    load_artifact(manifest_path)

    def test_training_contract_rejects_missing_feature_and_invalid_target(self) -> None:
        for candidate in (self.frame.drop(columns=["noise"]), self.frame.assign(target=2)):
            with self.assertRaises(ValueError):
                train_delivery_model(candidate)

    def test_fixed_report_is_deterministic_contract(self) -> None:
        report = fixed_report()
        self.assertIn("sha256_length=64", report)
        self.assertIn("roundtrip_probability_match=true", report)
        self.assertIn("invalid_schema=rejected:missing-or-additional-feature", report)
        self.assertIn("tampered_artifact=rejected:checksum-mismatch", report)
        self.assertTrue(report.endswith("invariants=full-pipeline-persisted,schema-validated,manifest-verified"))


if __name__ == "__main__":
    unittest.main()
