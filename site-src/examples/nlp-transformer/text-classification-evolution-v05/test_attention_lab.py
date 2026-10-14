import math
import unittest

import torch
from torch.nn import functional as F

from attention_lab import (
    AttentionClassifier,
    fit,
    hand_check,
    load_module,
    predict,
    run_validation,
    scaled_dot_product_attention,
    sinusoidal_position_encoding,
    V01,
)


class AttentionLabTests(unittest.TestCase):
    def test_hand_check_matches_manual_equal_scores(self):
        self.assertEqual(hand_check(), {
            "scale": round(1 / math.sqrt(2), 6),
            "full_first_weights": [0.5, 0.5],
            "full_first_output": [1.0, 2.0],
            "causal_first_weights": [1.0, 0.0],
            "causal_first_output": [2.0, 0.0],
        })

    def test_scaling_and_softmax_match_pytorch_sdpa(self):
        q = torch.tensor([[[1.0, 0.0], [0.0, 1.0]]])
        key_valid = torch.ones((1, 2), dtype=torch.bool)
        result, weights = scaled_dot_product_attention(q, q, q, key_valid)
        reference = F.scaled_dot_product_attention(q, q, q, dropout_p=0.0)
        torch.testing.assert_close(result, reference)
        self.assertTrue(torch.allclose(weights.sum(dim=-1), torch.ones((1, 2))))

    def test_padding_key_and_query_do_not_contribute(self):
        q = torch.tensor([[[1.0, 0.0], [0.0, 1.0], [9.0, 9.0]]])
        valid = torch.tensor([[True, True, False]])
        context, weights = scaled_dot_product_attention(q, q, q, valid)
        torch.testing.assert_close(weights[:, :, 2], torch.zeros((1, 3)))
        torch.testing.assert_close(weights[:, 2, :], torch.zeros((1, 3)))
        torch.testing.assert_close(context[:, 2, :], torch.zeros((1, 2)))
        self.assertTrue(torch.isfinite(context).all())

    def test_causal_mask_excludes_future_keys(self):
        q = torch.eye(3).unsqueeze(0)
        _, weights = scaled_dot_product_attention(q, q, q, torch.ones((1, 3), dtype=torch.bool), causal=True)
        self.assertEqual(weights[0, 0, 1].item(), 0.0)
        self.assertEqual(weights[0, 0, 2].item(), 0.0)
        self.assertEqual(weights[0, 1, 2].item(), 0.0)
        self.assertGreater(weights[0, 2, 0].item(), 0.0)

    def test_mask_rejects_invalid_rows_and_shapes(self):
        q = torch.ones((1, 2, 2))
        with self.assertRaisesRegex(ValueError, "first key"):
            scaled_dot_product_attention(q, q, q, torch.tensor([[False, True]]))
        with self.assertRaisesRegex(ValueError, "bool mask"):
            scaled_dot_product_attention(q, q, q, torch.ones((1, 2)))
        with self.assertRaisesRegex(ValueError, "shapes must match"):
            scaled_dot_product_attention(q, q, q[:, :1], torch.ones((1, 2), dtype=torch.bool))

    def test_position_encoding_has_shape_and_changes_by_position(self):
        enc = sinusoidal_position_encoding(4, 8)
        self.assertEqual(tuple(enc.shape), (4, 8))
        torch.testing.assert_close(enc[0, 0::2], torch.zeros(4))
        torch.testing.assert_close(enc[0, 1::2], torch.ones(4))
        self.assertFalse(torch.allclose(enc[0], enc[1]))
        with self.assertRaisesRegex(ValueError, "even dim"):
            sinusoidal_position_encoding(4, 3)

    def test_classifier_padding_and_position_switch(self):
        torch.manual_seed(7)
        model = AttentionClassifier(9)
        short = torch.tensor([[2, 3]], dtype=torch.long)
        padded = torch.tensor([[2, 3, 0, 0]], dtype=torch.long)
        logits_short, _ = model(short)
        logits_padded, weights = model(padded)
        torch.testing.assert_close(logits_short, logits_padded, atol=1e-6, rtol=1e-6)
        torch.testing.assert_close(weights[0, :, 2:], torch.zeros((4, 2)))
        without_position, _ = model(short, use_position=False)
        self.assertFalse(torch.allclose(logits_short, without_position))

    def test_attention_parameters_receive_gradients(self):
        model = AttentionClassifier(9)
        logits, _ = model(torch.tensor([[2, 3], [3, 2]], dtype=torch.long))
        F.cross_entropy(logits, torch.tensor([0, 1])).backward()
        self.assertIsNotNone(model.query.weight.grad)
        self.assertGreater(model.query.weight.grad.abs().sum().item(), 0.0)

    def test_fixed_corpus_and_sealed_test_contract(self):
        report = run_validation()
        self.assertEqual(report["project_version"], "0.5")
        self.assertEqual(report["corpus_sha256"], "8973927ed683f32cf92bb4a1483b960f3b8c09b0b8497bd0c5176891252b713c")
        self.assertEqual((report["train_rows"], report["validation_rows"]), (24, 8))
        self.assertEqual(report["test_status"], "sealed")
        self.assertEqual(report["hand_check"]["causal_first_weights"], [1.0, 0.0])

    def test_vocab_fit_only_on_train_and_validation_ids_only(self):
        v01 = load_module(V01, "v01_test")
        parts = v01.split_rows(v01.read_corpus())
        model, vocab = fit(parts["train"], epochs=2)
        predictions = predict(model, parts["validation"], vocab)
        self.assertEqual(set(predictions), {row["sample_id"] for row in parts["validation"]})
        self.assertNotIn("test", predictions)


if __name__ == "__main__":
    unittest.main()
