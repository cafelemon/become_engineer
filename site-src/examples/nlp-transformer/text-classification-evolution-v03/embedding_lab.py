"""Offline character-token Embedding + masked-mean text classifier (P3.3).

The tiny teaching corpus and split protocol are inherited from v0.1. The
complete CSV is read to verify its identity, but test rows are never fitted,
evaluated, or used for model selection in this entry point.
"""

from __future__ import annotations

import importlib.util
import json
import random
import re
import time
from collections import Counter
from pathlib import Path

import torch
from torch import nn

HERE = Path(__file__).resolve().parent
V01 = HERE.parent / "text-classification-evolution-v01" / "experiment.py"
LABELS = ("code", "plan")
SEED = 20261013
PAD = "<pad>"
UNK = "<unk>"


def load_v01():
    spec = importlib.util.spec_from_file_location("nlp_v01_experiment", V01)
    if spec is None or spec.loader is None:
        raise RuntimeError("v0.1 experiment is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tokenize(text: str) -> list[str]:
    """Keep Latin words/numbers together; use individual Han characters.

    This is a transparent teaching tokenizer, not Chinese word segmentation.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]|[^\s]", text.lower())


def build_vocab(train_rows: list[dict[str, str]]) -> dict[str, int]:
    if not train_rows:
        raise ValueError("training rows must not be empty")
    counts = Counter(token for row in train_rows for token in tokenize(row["text"]))
    return {token: index for index, token in enumerate((PAD, UNK, *sorted(counts)))}


def encode(text: str, vocab: dict[str, int], max_length: int = 48) -> list[int]:
    if max_length < 1:
        raise ValueError("max_length must be positive")
    if vocab.get(PAD) != 0 or vocab.get(UNK) != 1:
        raise ValueError("vocabulary must reserve pad=0 and unk=1")
    tokens = tokenize(text)[:max_length]
    return [vocab.get(token, 1) for token in tokens] or [1]


def batch(rows: list[dict[str, str]], vocab: dict[str, int], max_length: int = 48):
    if not rows:
        raise ValueError("batch must not be empty")
    sequences = [encode(row["text"], vocab, max_length) for row in rows]
    width = max(map(len, sequences))
    ids = torch.zeros((len(rows), width), dtype=torch.long)
    for index, sequence in enumerate(sequences):
        ids[index, :len(sequence)] = torch.tensor(sequence, dtype=torch.long)
    labels = torch.tensor([LABELS.index(row["label"]) for row in rows], dtype=torch.long)
    return ids, labels


class MeanEmbeddingClassifier(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int = 8) -> None:
        super().__init__()
        if vocab_size < 2 or embedding_dim < 1:
            raise ValueError("invalid model dimensions")
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.output = nn.Linear(embedding_dim, len(LABELS))

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        if token_ids.ndim != 2 or token_ids.dtype != torch.long:
            raise ValueError("token_ids must be a [batch, length] int64 tensor")
        if token_ids.shape[0] == 0 or token_ids.shape[1] == 0:
            raise ValueError("empty token batch")
        mask = token_ids.ne(0).unsqueeze(-1)
        embedded = self.embedding(token_ids)
        pooled = (embedded * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        return self.output(pooled)


def fit(train_rows: list[dict[str, str]], *, epochs: int = 80, learning_rate: float = 0.05):
    if epochs < 1 or learning_rate <= 0:
        raise ValueError("epochs and learning_rate must be positive")
    random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    vocab = build_vocab(train_rows)
    inputs, labels = batch(train_rows, vocab)
    model = MeanEmbeddingClassifier(len(vocab))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = criterion(model(inputs), labels)
        loss.backward()
        optimizer.step()
    return model, vocab


def predict(model: MeanEmbeddingClassifier, rows: list[dict[str, str]], vocab: dict[str, int]) -> dict[str, str]:
    if not rows:
        return {}
    model.eval()
    with torch.inference_mode():
        inputs, _ = batch(rows, vocab)
        indices = model(inputs).argmax(dim=1).tolist()
    return {row["sample_id"]: LABELS[index] for row, index in zip(rows, indices)}


def run_validation() -> dict:
    v01 = load_v01()
    rows = v01.read_corpus()
    partitions = v01.split_rows(rows)
    manifest = v01.build_manifest(rows, partitions)
    started = time.perf_counter()
    model, vocab = fit(partitions["train"])
    train_seconds = round(time.perf_counter() - started, 4)
    predictions = predict(model, partitions["validation"], vocab)
    metrics = v01.evaluate_validation(partitions, predictions)
    errors = [
        {"sample_id": row["sample_id"], "actual": row["label"], "predicted": predictions[row["sample_id"]]}
        for row in partitions["validation"] if predictions[row["sample_id"]] != row["label"]
    ]
    return {
        "project_version": "0.3",
        "corpus_sha256": manifest["corpus_sha256"],
        "split_seed": manifest["seed"],
        "train_ids": manifest["partitions"]["train"]["sample_ids"],
        "validation_ids": manifest["partitions"]["validation"]["sample_ids"],
        "train_rows": len(partitions["train"]),
        "validation_rows": len(partitions["validation"]),
        "test_status": "sealed",
        "tokenizer": "latin-words-and-han-characters-v1",
        "vocab_size": len(vocab),
        "model": "masked-mean-embedding-linear",
        "embedding_dim": 8,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "train_seconds": train_seconds,
        "seed": SEED,
        "epochs": 80,
        "learning_rate": 0.05,
        "model_validation": metrics,
        "validation_errors": errors,
    }


if __name__ == "__main__":
    print(json.dumps(run_validation(), ensure_ascii=False, sort_keys=True, indent=2))
