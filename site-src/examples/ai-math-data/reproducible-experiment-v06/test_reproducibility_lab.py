from __future__ import annotations

import unittest

from reproducibility_lab import ExperimentConfig, build_manifest, dataset_fingerprint, fixed_report, verify_manifest


class ReproducibilityLabTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ExperimentConfig(7, 0.5, "v1", "stratified")
        self.rows = ({"sample_id": "b", "label": 0}, {"sample_id": "a", "label": 1})
        self.artifacts = {"metrics.json": b'{"accuracy":1.0}\n'}

    def test_dataset_fingerprint_is_stable_across_row_order(self) -> None:
        self.assertEqual(dataset_fingerprint(self.rows), dataset_fingerprint(tuple(reversed(self.rows))))

    def test_dataset_fingerprint_changes_with_content(self) -> None:
        changed = ({"sample_id": "b", "label": 1}, {"sample_id": "a", "label": 1})
        self.assertNotEqual(dataset_fingerprint(self.rows), dataset_fingerprint(changed))

    def test_manifest_contains_config_data_metrics_and_artifacts(self) -> None:
        manifest = build_manifest(self.config, self.rows, {"accuracy": 1.0}, self.artifacts, code_revision="abc123")
        self.assertEqual(manifest["code_revision"], "abc123")
        self.assertEqual(manifest["metrics"], {"accuracy": 1.0})
        self.assertEqual(set(manifest["artifacts"]), {"metrics.json"})

    def test_verification_detects_config_data_and_artifact_changes(self) -> None:
        manifest = build_manifest(self.config, self.rows, {}, self.artifacts, code_revision="abc123")
        self.assertEqual(verify_manifest(manifest, ExperimentConfig(8, 0.5, "v1", "stratified"), self.rows, self.artifacts)[1], ("config",))
        changed_rows = ({"sample_id": "a", "label": 0}, {"sample_id": "b", "label": 0})
        self.assertEqual(verify_manifest(manifest, self.config, changed_rows, self.artifacts)[1], ("data",))
        self.assertEqual(verify_manifest(manifest, self.config, self.rows, {"metrics.json": b"changed"})[1], ("artifacts",))

    def test_invalid_dataset_and_artifact_names_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            dataset_fingerprint(({"label": 1},))
        with self.assertRaises(ValueError):
            dataset_fingerprint(({"sample_id": "a"}, {"sample_id": "a"}))
        with self.assertRaises(ValueError):
            build_manifest(self.config, self.rows, {}, {"../secret": b"x"}, code_revision="abc")

    def test_fixed_report_is_deterministic(self) -> None:
        report = fixed_report()
        self.assertIn("verify=pass", report)
        self.assertIn("tampered=artifacts", report)
        self.assertIn("artifact_count=2", report)
        self.assertTrue(report.endswith("invariants=canonical-config,stable-data-order,artifact-integrity"))


if __name__ == "__main__":
    unittest.main()
