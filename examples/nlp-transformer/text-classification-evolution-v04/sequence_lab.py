"""Small offline GRU/CNN text baselines on the v0.1 split (P3.4)."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

import torch
from torch import nn

HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V01 = load_module("nlp_v01", HERE.parent / "text-classification-evolution-v01" / "experiment.py")
V03 = load_module("nlp_v03", HERE.parent / "text-classification-evolution-v03" / "embedding_lab.py")


class SequenceClassifier(nn.Module):
    def __init__(self, vocab_size: int, architecture: str, embedding_dim: int = 8, hidden_dim: int = 8):
        super().__init__()
        if architecture not in {"gru", "cnn"}:
            raise ValueError("architecture must be gru or cnn")
        if vocab_size < 2 or embedding_dim < 1 or hidden_dim < 1:
            raise ValueError("invalid dimensions")
        self.architecture = architecture
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.encoder = nn.GRU(embedding_dim, hidden_dim, batch_first=True) if architecture == "gru" else nn.Conv1d(embedding_dim, hidden_dim, 3, padding=1)
        self.output = nn.Linear(hidden_dim, 2)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        if token_ids.ndim != 2 or token_ids.dtype != torch.long or token_ids.numel() == 0:
            raise ValueError("token_ids must be nonempty [batch,length] int64")
        lengths = token_ids.ne(0).sum(dim=1)
        if torch.any(lengths == 0):
            raise ValueError("each sequence needs a non-padding token")
        embedded = self.embedding(token_ids)
        if self.architecture == "gru":
            packed = nn.utils.rnn.pack_padded_sequence(embedded, lengths.cpu(), batch_first=True, enforce_sorted=False)
            _, hidden = self.encoder(packed)
            pooled = hidden[-1]
        else:
            features = torch.relu(self.encoder(embedded.transpose(1, 2))).transpose(1, 2)
            pooled = features.masked_fill(~token_ids.ne(0).unsqueeze(-1), torch.finfo(features.dtype).min).amax(dim=1)
        return self.output(pooled)


def fit(train_rows: list[dict[str, str]], architecture: str, *, epochs: int = 80, learning_rate: float = 0.05):
    if not train_rows or epochs < 1 or learning_rate <= 0:
        raise ValueError("invalid training configuration")
    torch.manual_seed(V03.SEED)
    torch.set_num_threads(1)
    vocab = V03.build_vocab(train_rows)
    inputs, labels = V03.batch(train_rows, vocab)
    model = SequenceClassifier(len(vocab), architecture)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.CrossEntropyLoss()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = loss_fn(model(inputs), labels)
        loss.backward()
        optimizer.step()
    return model, vocab


def predict(model: SequenceClassifier, rows: list[dict[str, str]], vocab: dict[str, int]) -> dict[str, str]:
    if not rows:
        return {}
    model.eval()
    with torch.inference_mode():
        inputs, _ = V03.batch(rows, vocab)
        predictions = model(inputs).argmax(dim=1).tolist()
    return {row["sample_id"]: V03.LABELS[index] for row, index in zip(rows, predictions)}


def run_validation() -> dict:
    rows = V01.read_corpus()
    partitions = V01.split_rows(rows)
    manifest = V01.build_manifest(rows, partitions)
    results = {}
    for architecture in ("gru", "cnn"):
        start = time.perf_counter()
        model, vocab = fit(partitions["train"], architecture)
        train_seconds = round(time.perf_counter() - start, 4)
        start = time.perf_counter()
        predictions = predict(model, partitions["validation"], vocab)
        inference_seconds = round(time.perf_counter() - start, 4)
        results[architecture] = {
            "validation": V01.evaluate_validation(partitions, predictions),
            "errors": [row["sample_id"] for row in partitions["validation"] if predictions[row["sample_id"]] != row["label"]],
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            "train_seconds": train_seconds,
            "inference_seconds": inference_seconds,
        }
    return {
        "project_version": "0.4",
        "corpus_sha256": manifest["corpus_sha256"],
        "split_seed": manifest["seed"],
        "train_ids": manifest["partitions"]["train"]["sample_ids"],
        "validation_ids": manifest["partitions"]["validation"]["sample_ids"],
        "train_rows": len(partitions["train"]),
        "validation_rows": len(partitions["validation"]),
        "test_status": "sealed",
        "tokenizer": "latin-words-and-han-characters-v1",
        "epochs": 80,
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_validation(), ensure_ascii=False, sort_keys=True, indent=2))
