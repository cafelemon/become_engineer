"""Offline, inspectable scaled-dot-product attention for text classification."""

from __future__ import annotations

import importlib.util
import json
import math
import random
import time
from pathlib import Path

import torch
from torch import nn

HERE = Path(__file__).resolve().parent
V01 = HERE.parent / "text-classification-evolution-v01" / "experiment.py"
V03 = HERE.parent / "text-classification-evolution-v03" / "embedding_lab.py"
SEED = 20261013
EMBED_DIM = 8


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"required earlier lesson missing: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sinusoidal_position_encoding(length: int, dim: int, *, device=None, dtype=torch.float32) -> torch.Tensor:
    """Return [length, dim] fixed sine/cosine positions; dim must be even."""
    if length < 1 or dim < 2 or dim % 2:
        raise ValueError("position encoding requires positive length and even dim >= 2")
    positions = torch.arange(length, dtype=dtype, device=device).unsqueeze(1)
    frequencies = torch.exp(torch.arange(0, dim, 2, dtype=dtype, device=device) * (-math.log(10000.0) / dim))
    result = torch.empty((length, dim), dtype=dtype, device=device)
    result[:, 0::2] = torch.sin(positions * frequencies)
    result[:, 1::2] = torch.cos(positions * frequencies)
    return result


def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    key_valid: torch.Tensor,
    *,
    causal: bool = False,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return contextual values and auditable weights; True in mask means allowed."""
    if query.ndim != 3 or key.ndim != 3 or value.ndim != 3:
        raise ValueError("query/key/value must be [batch,length,dim]")
    if query.shape != key.shape or query.shape != value.shape:
        raise ValueError("self-attention query/key/value shapes must match")
    batch_size, length, dim = query.shape
    if batch_size < 1 or length < 1 or dim < 1:
        raise ValueError("empty attention tensor")
    if key_valid.shape != (batch_size, length) or key_valid.dtype != torch.bool:
        raise ValueError("key_valid must be a [batch,length] bool mask")
    if not bool(key_valid[:, 0].all()):
        raise ValueError("first key must be valid; every query needs an allowed key")
    scores = query @ key.transpose(-2, -1) / math.sqrt(dim)
    allowed = key_valid.unsqueeze(1).expand(batch_size, length, length)
    if causal:
        allowed = allowed & torch.ones((length, length), dtype=torch.bool, device=query.device).tril().unsqueeze(0)
    weights = torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
    context = weights @ value
    # Padded query rows are not meaningful and must not enter pooling.
    query_valid = key_valid.unsqueeze(-1)
    return context.masked_fill(~query_valid, 0.0), weights.masked_fill(~key_valid.unsqueeze(-1), 0.0)


class AttentionClassifier(nn.Module):
    def __init__(self, vocab_size: int, dim: int = EMBED_DIM):
        super().__init__()
        if vocab_size < 2 or dim < 2 or dim % 2:
            raise ValueError("invalid vocabulary size or attention dimension")
        self.embedding = nn.Embedding(vocab_size, dim, padding_idx=0)
        self.query = nn.Linear(dim, dim, bias=False)
        self.key = nn.Linear(dim, dim, bias=False)
        self.value = nn.Linear(dim, dim, bias=False)
        self.output = nn.Linear(dim, 2)

    def forward(self, token_ids: torch.Tensor, *, causal: bool = False, use_position: bool = True):
        if token_ids.ndim != 2 or token_ids.dtype != torch.long or token_ids.numel() == 0:
            raise ValueError("token IDs must be a nonempty [batch,length] int64 tensor")
        valid = token_ids.ne(0)
        if not bool(valid[:, 0].all()):
            raise ValueError("each sequence must begin with a non-padding token")
        embedded = self.embedding(token_ids)
        if use_position:
            embedded = embedded + sinusoidal_position_encoding(token_ids.shape[1], embedded.shape[-1], device=embedded.device, dtype=embedded.dtype)
        context, weights = scaled_dot_product_attention(self.query(embedded), self.key(embedded), self.value(embedded), valid, causal=causal)
        pooled = context.sum(dim=1) / valid.sum(dim=1, keepdim=True)
        return self.output(pooled), weights


def fit(train_rows: list[dict[str, str]], *, epochs: int = 50, learning_rate: float = 0.03):
    if epochs < 1 or learning_rate <= 0:
        raise ValueError("epochs and learning_rate must be positive")
    v03 = load_module(V03, "nlp_v03_embedding")
    random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    vocab = v03.build_vocab(train_rows)
    tokens, labels = v03.batch(train_rows, vocab)
    model = AttentionClassifier(len(vocab))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        logits, _ = model(tokens)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
    return model, vocab


def predict(model: AttentionClassifier, rows: list[dict[str, str]], vocab: dict[str, int]) -> dict[str, str]:
    if not rows:
        return {}
    v03 = load_module(V03, "nlp_v03_predict")
    model.eval()
    with torch.inference_mode():
        tokens, _ = v03.batch(rows, vocab)
        logits, _ = model(tokens)
        classes = logits.argmax(dim=-1).tolist()
    return {row["sample_id"]: v03.LABELS[index] for row, index in zip(rows, classes)}


def hand_check() -> dict:
    """Two keys with equal scores: visible weight changes from 1/2 to 1/1."""
    q = torch.tensor([[[1.0, 0.0], [1.0, 0.0]]])
    k = q.clone()
    v = torch.tensor([[[2.0, 0.0], [0.0, 4.0]]])
    full, full_weights = scaled_dot_product_attention(q, k, v, torch.tensor([[True, True]]))
    causal, causal_weights = scaled_dot_product_attention(q, k, v, torch.tensor([[True, True]]), causal=True)
    return {"scale": round(1 / math.sqrt(2), 6), "full_first_weights": [round(x, 3) for x in full_weights[0, 0].tolist()], "full_first_output": [round(x, 3) for x in full[0, 0].tolist()], "causal_first_weights": [round(x, 3) for x in causal_weights[0, 0].tolist()], "causal_first_output": [round(x, 3) for x in causal[0, 0].tolist()]}


def run_validation() -> dict:
    v01 = load_module(V01, "nlp_v01_experiment")
    rows = v01.read_corpus()
    partitions = v01.split_rows(rows)
    manifest = v01.build_manifest(rows, partitions)
    started = time.perf_counter()
    model, vocab = fit(partitions["train"])
    train_seconds = round(time.perf_counter() - started, 4)
    predictions = predict(model, partitions["validation"], vocab)
    metrics = v01.evaluate_validation(partitions, predictions)
    errors = [{"sample_id": row["sample_id"], "actual": row["label"], "predicted": predictions[row["sample_id"]]} for row in partitions["validation"] if predictions[row["sample_id"]] != row["label"]]
    return {
        "project_version": "0.5",
        "corpus_sha256": manifest["corpus_sha256"],
        "split_seed": manifest["seed"],
        "train_ids": manifest["partitions"]["train"]["sample_ids"],
        "validation_ids": manifest["partitions"]["validation"]["sample_ids"],
        "train_rows": len(partitions["train"]),
        "validation_rows": len(partitions["validation"]),
        "test_status": "sealed",
        "tokenizer": "latin-words-and-han-characters-v1",
        "vocab_size": len(vocab),
        "model": "single-head-scaled-dot-product-attention-classifier",
        "attention_dim": EMBED_DIM,
        "position_encoding": "fixed-sinusoidal",
        "classification_mask": "padding-only-bidirectional",
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "train_seconds": train_seconds,
        "seed": SEED,
        "epochs": 50,
        "learning_rate": 0.03,
        "hand_check": hand_check(),
        "model_validation": metrics,
        "validation_errors": errors,
    }


if __name__ == "__main__":
    print(json.dumps(run_validation(), ensure_ascii=False, sort_keys=True, indent=2))
