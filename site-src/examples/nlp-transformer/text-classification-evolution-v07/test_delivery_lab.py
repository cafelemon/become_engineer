import tempfile
import unittest
from pathlib import Path

from delivery_lab import (
    EXPECTED_CORPUS_SHA,
    candidate,
    collect_validation,
    load_module,
    model_card,
    protocol_from_manifest,
    score_rows,
    select_candidate,
    verify_report_protocol,
    finalize,
)


class DeliveryLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = collect_validation()  # Validation only; no test predictions.

    def test_fixed_protocol_and_all_six_release_candidates(self):
        self.assertEqual(self.plan["protocol"]["corpus_sha256"], EXPECTED_CORPUS_SHA)
        self.assertEqual(len(self.plan["candidates"]), 6)
        self.assertEqual(len(self.plan["protocol"]["test_ids"]), 8)
        self.assertEqual(self.plan["test_status"], "sealed_before_selection")
        for entry in self.plan["candidates"]:
            self.assertTrue(entry["eligible_for_release"])
            self.assertGreater(entry["parameter_count"], 0)
            self.assertGreaterEqual(entry["validation_run_seconds_observed"], 0)

    def test_ablation_variants_are_not_release_candidates(self):
        ids = {item["candidate_id"] for item in self.plan["candidates"]}
        self.assertNotIn("no_position", ids)
        self.assertNotIn("no_key_padding_mask", ids)
        self.assertFalse(self.plan["ablations_not_candidates"]["no_position"]["eligible_for_release"])
        self.assertFalse(self.plan["ablations_not_candidates"]["no_key_padding_mask"]["eligible_for_release"])

    def test_predeclared_rule_selects_full_encoder(self):
        selected = select_candidate(self.plan)
        self.assertEqual(selected["candidate_id"], "v06-encoder-full")
        self.assertEqual(selected["validation"]["macro_f1"], 1.0)

    def test_tie_breaks_lower_parameter_then_id(self):
        metrics = {"accuracy": 0.75, "macro_f1": 0.75, "confusion": {"code": {"code": 3, "plan": 1}, "plan": {"code": 1, "plan": 3}}}
        fake = {"candidates": [candidate("z", "test", metrics, [], 20, 0, 0.1),
                                candidate("b", "test", metrics, [], 10, 0, 0.1),
                                candidate("a", "test", metrics, [], 10, 0, 0.1)]}
        self.assertEqual(select_candidate(fake)["candidate_id"], "a")

    def test_changed_corpus_is_blocked(self):
        v01 = load_module("v01")
        rows = v01.read_corpus()
        rows[0] = dict(rows[0], text=rows[0]["text"] + "新增")
        with self.assertRaisesRegex(ValueError, "fingerprint changed"):
            protocol_from_manifest(v01, rows, v01.split_rows(rows))

    def test_mismatched_split_or_unsealed_report_is_blocked(self):
        report = {**self.plan["protocol"], "test_status": "sealed"}
        verify_report_protocol(report, self.plan["protocol"], "v03")
        with self.assertRaisesRegex(ValueError, "train_ids"):
            verify_report_protocol({**report, "train_ids": []}, self.plan["protocol"], "v03")
        with self.assertRaisesRegex(ValueError, "tested before selection"):
            verify_report_protocol({**report, "test_status": "opened"}, self.plan["protocol"], "v03")

    def test_score_rows_rejects_missing_and_extra_ids(self):
        rows = [{"sample_id": "a", "label": "code"}, {"sample_id": "b", "label": "plan"}]
        with self.assertRaisesRegex(ValueError, "exactly"):
            score_rows(rows, {"a": "code"})
        with self.assertRaisesRegex(ValueError, "known labels"):
            score_rows(rows, {"a": "code", "b": "other"})

    def test_score_rows_confusion_and_macro_f1(self):
        rows = [{"sample_id": "a", "label": "code"}, {"sample_id": "b", "label": "plan"}]
        result = score_rows(rows, {"a": "code", "b": "code"})
        self.assertEqual(result["accuracy"], 0.5)
        self.assertAlmostEqual(result["macro_f1"], 1 / 3)
        self.assertEqual(result["error_ids"], ["b"])

    def test_model_card_marks_pretraining_unrun(self):
        selected = select_candidate(self.plan)
        synthetic = {"test": {"accuracy": 0.5, "macro_f1": 1 / 3, "error_ids": ["toy"]}}
        card = model_card(self.plan, selected, synthetic)
        self.assertIn("未下载、微调或测量任何预训练权重", card)
        self.assertIn("no_key_padding_mask", str(self.plan["ablations_not_candidates"]))

    def test_finalize_refuses_existing_output_before_opening_test(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "old.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                finalize(path)
            self.assertEqual((path / "old.txt").read_text(encoding="utf-8"), "keep")
            self.assertFalse((path / "test-opened.json").exists())


if __name__ == "__main__":
    unittest.main()
