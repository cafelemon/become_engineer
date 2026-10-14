"""Contract checks for P3.3; run with ``python -m unittest -v``."""

import unittest

import torch

from embedding_lab import (
    LABELS, MeanEmbeddingClassifier, batch, build_vocab, encode, fit,
    load_v01, predict, run_validation, tokenize,
)


class EmbeddingLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v01 = load_v01()
        cls.partitions = v01.split_rows(v01.read_corpus())

    def test_tokenizer_keeps_latin_words_and_splits_han(self):
        self.assertEqual(tokenize("Python 函数42?"), ["python", "函", "数", "42", "?"])

    def test_vocabulary_is_train_only_and_has_reserved_ids(self):
        vocab = build_vocab(self.partitions["train"])
        self.assertEqual((vocab["<pad>"], vocab["<unk>"]), (0, 1))
        self.assertEqual(encode("zzzxqv", vocab), [1])
        self.assertNotIn("zzzxqv", vocab)
        self.assertNotIn("python", vocab)  # Appears outside the training split.

    def test_batch_padding_and_labels(self):
        rows = self.partitions["train"][:2]
        ids, labels = batch(rows, build_vocab(self.partitions["train"]))
        self.assertEqual(ids.shape[0], 2)
        self.assertEqual(labels.dtype, torch.long)
        self.assertEqual(labels.tolist(), [LABELS.index(row["label"]) for row in rows])

    def test_padding_does_not_change_pooled_logits(self):
        model = MeanEmbeddingClassifier(8, 4)
        model.eval()
        with torch.inference_mode():
            one = model(torch.tensor([[2, 3]], dtype=torch.long))
            padded = model(torch.tensor([[2, 3, 0, 0]], dtype=torch.long))
        torch.testing.assert_close(one, padded)

    def test_forward_rejects_wrong_shape_and_dtype(self):
        model = MeanEmbeddingClassifier(8, 4)
        with self.assertRaises(ValueError):
            model(torch.tensor([2, 3], dtype=torch.long))
        with self.assertRaises(ValueError):
            model(torch.tensor([[2.0, 3.0]]))

    def test_embedding_receives_gradient_but_pad_row_does_not(self):
        model = MeanEmbeddingClassifier(8, 4)
        loss = torch.nn.CrossEntropyLoss()(model(torch.tensor([[2, 3, 0]], dtype=torch.long)), torch.tensor([0]))
        loss.backward()
        self.assertGreater(model.embedding.weight.grad[2].abs().sum().item(), 0)
        self.assertEqual(model.embedding.weight.grad[0].abs().sum().item(), 0)

    def test_fit_and_validation_predictions_are_deterministic(self):
        train, validation = self.partitions["train"], self.partitions["validation"]
        model_a, vocab_a = fit(train, epochs=8)
        model_b, vocab_b = fit(train, epochs=8)
        self.assertEqual(vocab_a, vocab_b)
        self.assertEqual(predict(model_a, validation, vocab_a), predict(model_b, validation, vocab_b))

    def test_predictions_use_only_requested_ids(self):
        model, vocab = fit(self.partitions["train"], epochs=8)
        predictions = predict(model, self.partitions["validation"], vocab)
        self.assertEqual(set(predictions), {row["sample_id"] for row in self.partitions["validation"]})

    def test_report_keeps_test_sealed_and_uses_v01_metrics(self):
        report = run_validation()
        self.assertEqual(report["test_status"], "sealed")
        self.assertEqual(report["train_rows"], 24)
        self.assertEqual(report["validation_rows"], 8)
        self.assertIn("accuracy", report["model_validation"])
        self.assertEqual(len(report["validation_ids"]), 8)
        self.assertEqual(report["split_seed"], load_v01().SEED)
        self.assertNotIn("test_metrics", report)


if __name__ == "__main__":
    unittest.main()
