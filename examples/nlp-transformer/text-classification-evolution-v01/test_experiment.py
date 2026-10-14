import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from experiment import CORPUS, build_manifest, evaluate_validation, read_corpus, split_rows, write_artifacts


class TextTaskContractTests(unittest.TestCase):
    def setUp(self):
        self.rows = read_corpus()
        self.parts = split_rows(self.rows)

    def test_corpus_counts_and_schema(self):
        self.assertEqual(len(self.rows), 40)
        self.assertEqual(Counter(row["label"] for row in self.rows), {"code": 20, "plan": 20})

    def test_split_is_stratified_and_disjoint(self):
        for name, per_class in (("train", 12), ("validation", 4), ("test", 4)):
            self.assertEqual(Counter(row["label"] for row in self.parts[name]), {"code": per_class, "plan": per_class})
        ids = [row["sample_id"] for partition in self.parts.values() for row in partition]
        self.assertEqual(len(ids), len(set(ids)))

    def test_input_order_does_not_change_assignment(self):
        self.assertEqual(self.parts, split_rows(list(reversed(self.rows))))

    def test_seed_change_changes_assignment(self):
        self.assertNotEqual(self.parts, split_rows(self.rows, "different-seed"))

    def test_duplicate_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text(CORPUS.read_text(encoding="utf-8").replace("P20,plan", "P19,plan"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate sample_id"):
                read_corpus(path)

    def test_duplicate_text_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text(CORPUS.read_text(encoding="utf-8").replace("学习清单太长怎样排优先级", "每天学习半小时如何安排"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate text"):
                read_corpus(path)

    def test_manifest_tracks_corpus_and_policy(self):
        manifest = build_manifest(self.rows, self.parts)
        self.assertEqual(len(manifest["corpus_sha256"]), 64)
        self.assertIn("test sealed", manifest["policy"])
        self.assertEqual(manifest["partitions"]["train"]["class_counts"], {"code": 12, "plan": 12})

    def test_validation_metrics_for_constant_baseline(self):
        predictions = {row["sample_id"]: "code" for row in self.parts["validation"]}
        result = evaluate_validation(self.parts, predictions)
        self.assertEqual(result["accuracy"], 0.5)
        self.assertAlmostEqual(result["macro_f1"], 1 / 3)
        self.assertEqual(result["confusion"], {"code": {"code": 4, "plan": 0}, "plan": {"code": 4, "plan": 0}})

    def test_validation_rejects_test_id_and_invalid_label(self):
        predictions = {row["sample_id"]: "code" for row in self.parts["validation"]}
        predictions[next(iter(predictions))] = "unknown"
        with self.assertRaisesRegex(ValueError, "unknown label"):
            evaluate_validation(self.parts, predictions)
        predictions = {row["sample_id"]: "code" for row in self.parts["test"]}
        with self.assertRaisesRegex(ValueError, "validation IDs"):
            evaluate_validation(self.parts, predictions)

    def test_artifacts_match_manifest_and_refuse_overwrite(self):
        manifest = build_manifest(self.rows, self.parts)
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "artifacts"
            write_artifacts(output, self.parts, manifest)
            with (output / "test.csv").open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 8)
            with self.assertRaises(FileExistsError):
                write_artifacts(output, self.parts, manifest)


if __name__ == "__main__":
    unittest.main()
