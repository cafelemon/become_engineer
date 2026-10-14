import unittest

import torch

import sequence_lab as lab


class SequenceLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.partitions = lab.V01.split_rows(lab.V01.read_corpus())
        cls.vocab = lab.V03.build_vocab(cls.partitions["train"])

    def test_split_is_reused(self):
        self.assertEqual([len(self.partitions[key]) for key in ("train", "validation", "test")], [24, 8, 8])

    def test_vocab_uses_training_only(self):
        self.assertEqual(self.vocab, lab.V03.build_vocab(self.partitions["train"]))
        self.assertEqual(self.vocab[lab.V03.PAD], 0)

    def test_architecture_rejected(self):
        with self.assertRaises(ValueError):
            lab.SequenceClassifier(len(self.vocab), "unknown")

    def test_shapes(self):
        tokens = torch.tensor([[2, 3, 0], [3, 2, 4]], dtype=torch.long)
        for name in ("gru", "cnn"):
            self.assertEqual(tuple(lab.SequenceClassifier(len(self.vocab), name)(tokens).shape), (2, 2))

    def test_input_contract(self):
        model = lab.SequenceClassifier(len(self.vocab), "gru")
        with self.assertRaises(ValueError):
            model(torch.ones(2, 3, dtype=torch.float32))
        with self.assertRaises(ValueError):
            model(torch.zeros(1, 3, dtype=torch.long))

    def test_padding_does_not_change_logits(self):
        for name in ("gru", "cnn"):
            model = lab.SequenceClassifier(len(self.vocab), name)
            before = model(torch.tensor([[2, 3]], dtype=torch.long))
            after = model(torch.tensor([[2, 3, 0, 0]], dtype=torch.long))
            self.assertTrue(torch.allclose(before, after, atol=1e-6), name)

    def test_gradient_flows(self):
        model = lab.SequenceClassifier(len(self.vocab), "cnn")
        model(torch.tensor([[2, 3]], dtype=torch.long)).sum().backward()
        self.assertIsNotNone(model.embedding.weight.grad)

    def test_validation_only_prediction_ids(self):
        model, vocab = lab.fit(self.partitions["train"], "gru", epochs=2)
        predictions = lab.predict(model, self.partitions["validation"], vocab)
        self.assertEqual(set(predictions), {row["sample_id"] for row in self.partitions["validation"]})

    def test_report_seals_test_and_records_cost(self):
        report = lab.run_validation()
        self.assertEqual(report["test_status"], "sealed")
        self.assertEqual((report["train_rows"], report["validation_rows"]), (24, 8))
        self.assertNotIn("test_metrics", report)
        for name in ("gru", "cnn"):
            self.assertGreater(report["results"][name]["parameter_count"], 0)
            self.assertIn("accuracy", report["results"][name]["validation"])


if __name__ == "__main__":
    unittest.main()
