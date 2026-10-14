"""P3.5 encoder/ablation contract tests; no test-set evaluation."""

import unittest

import torch

from transformer_lab import (
    EPOCHS, V03, V05, TinyTransformerClassifier, fit, load_module,
    position_encoding, predict, run_validation,
)


class TransformerLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from transformer_lab import V01
        cls.v01 = load_module(V01, "v01_for_v06_tests")
        cls.v03 = load_module(V03, "v03_for_v06_tests")
        cls.parts = cls.v01.split_rows(cls.v01.read_corpus())
        cls.vocab = cls.v03.build_vocab(cls.parts["train"])

    def test_position_encoding_reuses_v05_interface(self):
        v05 = load_module(V05, "v05_for_v06_tests")
        actual = position_encoding(4, 16, device=torch.device("cpu"), dtype=torch.float32)
        expected = v05.sinusoidal_position_encoding(4, 16).unsqueeze(0)
        torch.testing.assert_close(actual, expected)
        self.assertFalse(torch.equal(actual[0, 0], actual[0, 1]))

    def test_encoder_shapes_and_parameter_count(self):
        model = TinyTransformerClassifier(len(self.vocab))
        output = model(torch.tensor([[2, 3, 0], [2, 4, 5]], dtype=torch.long))
        self.assertEqual(tuple(output.shape), (2, 2))
        self.assertGreater(sum(p.numel() for p in model.parameters()), len(self.vocab) * 16)

    def test_key_padding_mask_keeps_logits_stable(self):
        torch.manual_seed(7)
        model = TinyTransformerClassifier(10).eval()
        with torch.inference_mode():
            short = model(torch.tensor([[2, 3]], dtype=torch.long))
            padded = model(torch.tensor([[2, 3, 0, 0]], dtype=torch.long))
        torch.testing.assert_close(short, padded, atol=1e-5, rtol=1e-5)

    def test_no_key_padding_mask_changes_padded_result(self):
        torch.manual_seed(7)
        model = TinyTransformerClassifier(10, use_key_padding_mask=False).eval()
        with torch.inference_mode():
            short = model(torch.tensor([[2, 3]], dtype=torch.long))
            padded = model(torch.tensor([[2, 3, 0, 0]], dtype=torch.long))
        self.assertFalse(torch.allclose(short, padded, atol=1e-5, rtol=1e-5))

    def test_without_position_permutation_has_same_logits(self):
        torch.manual_seed(7)
        model = TinyTransformerClassifier(10, use_position=False).eval()
        with torch.inference_mode():
            first = model(torch.tensor([[2, 3, 4]], dtype=torch.long))
            reordered = model(torch.tensor([[4, 3, 2]], dtype=torch.long))
        torch.testing.assert_close(first, reordered, atol=1e-5, rtol=1e-5)

    def test_rejects_bad_dtype_shape_and_all_padding(self):
        model = TinyTransformerClassifier(10)
        for ids in (torch.tensor([2, 3]), torch.tensor([[2.0, 3.0]]), torch.tensor([[0, 0]])):
            with self.assertRaises(ValueError):
                model(ids)

    def test_encoder_receives_gradient(self):
        model = TinyTransformerClassifier(10)
        loss = torch.nn.CrossEntropyLoss()(model(torch.tensor([[2, 3, 0]], dtype=torch.long)), torch.tensor([0]))
        loss.backward()
        self.assertGreater(model.encoder.layers[0].self_attn.in_proj_weight.grad.abs().sum().item(), 0)

    def test_train_only_vocab_and_deterministic_short_fit(self):
        self.assertNotIn("python", self.vocab)  # This corpus puts it outside train.
        model_a = fit(self.parts["train"], self.vocab, use_position=True, use_key_padding_mask=True, epochs=2)
        model_b = fit(self.parts["train"], self.vocab, use_position=True, use_key_padding_mask=True, epochs=2)
        self.assertEqual(predict(model_a, self.parts["validation"], self.vocab),
                         predict(model_b, self.parts["validation"], self.vocab))

    def test_report_three_variants_same_split_and_no_test_metric(self):
        report = run_validation()
        self.assertEqual(report["test_status"], "sealed")
        self.assertEqual((report["train_rows"], report["validation_rows"]), (24, 8))
        self.assertEqual(report["configuration"]["epochs"], EPOCHS)
        self.assertEqual(set(report["variants"]), {"full", "no_position", "no_key_padding_mask"})
        self.assertEqual(report["split_seed"], self.v01.SEED)
        self.assertEqual(len(report["validation_ids"]), 8)
        for variant in report["variants"].values():
            self.assertIn("macro_f1", variant["model_validation"])
            self.assertGreater(variant["validation_batch_ms_median"], 0)
            self.assertNotIn("test_metrics", variant)


if __name__ == "__main__":
    unittest.main()
