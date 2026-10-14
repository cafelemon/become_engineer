"""CPU-only Transformer encoder classification and controlled ablations (P3.5)."""

from __future__ import annotations

import importlib.util
import json
import random
import statistics
import time
from functools import lru_cache
from pathlib import Path

import torch
from torch import nn

HERE = Path(__file__).resolve().parent
V01 = HERE.parent / "text-classification-evolution-v01" / "experiment.py"
V03 = HERE.parent / "text-classification-evolution-v03" / "embedding_lab.py"
V05 = HERE.parent / "text-classification-evolution-v05" / "attention_lab.py"
SEED = 20261014
MAX_LENGTH = 48
EPOCHS = 24
LEARNING_RATE = 0.02


@lru_cache(maxsize=8)
def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing project contract: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def position_encoding(length: int, width: int, *, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    """Reuse v0.5's fixed positions; add a batch axis for TransformerEncoder."""
    v05 = load_module(V05, "nlp_v05_position_for_v06")
    return v05.sinusoidal_position_encoding(length, width, device=device, dtype=dtype).unsqueeze(0)


class TinyTransformerClassifier(nn.Module):
    def __init__(self, vocab_size: int, *, width: int = 16, heads: int = 2,
                 use_position: bool = True, use_key_padding_mask: bool = True) -> None:
        super().__init__()
        if vocab_size < 2 or width < 2 or width % 2 or heads < 1 or width % heads:
            raise ValueError("invalid Transformer dimensions")
        self.use_position = use_position
        self.use_key_padding_mask = use_key_padding_mask
        self.embedding = nn.Embedding(vocab_size, width, padding_idx=0)
        layer = nn.TransformerEncoderLayer(d_model=width, nhead=heads, dim_feedforward=width * 2,
                                           dropout=0.0, batch_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=1, enable_nested_tensor=False)
        self.classifier = nn.Linear(width, 2)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        if token_ids.ndim != 2 or token_ids.dtype != torch.long or min(token_ids.shape) < 1:
            raise ValueError("token_ids must be nonempty [batch,length] int64")
        valid = token_ids.ne(0)
        if not valid.any(dim=1).all():
            raise ValueError("each sample needs at least one real token")
        hidden = self.embedding(token_ids)
        if self.use_position:
            hidden = hidden + position_encoding(token_ids.shape[1], hidden.shape[2], device=hidden.device, dtype=hidden.dtype)
        # PyTorch's key-padding mask is True for positions that must be ignored.
        key_padding_mask = ~valid if self.use_key_padding_mask else None
        encoded = self.encoder(hidden, src_key_padding_mask=key_padding_mask)
        # Keep the same pooling policy in all three variants: only attention masking changes.
        pooled = (encoded * valid.unsqueeze(-1)).sum(dim=1) / valid.sum(dim=1, keepdim=True)
        return self.classifier(pooled)


def fit(train_rows: list[dict[str, str]], vocab: dict[str, int], *, use_position: bool,
        use_key_padding_mask: bool, epochs: int = EPOCHS) -> TinyTransformerClassifier:
    if not train_rows or epochs < 1:
        raise ValueError("training rows and epochs must be positive")
    v03 = load_module(V03, "nlp_v03_for_v06")
    random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    model = TinyTransformerClassifier(len(vocab), use_position=use_position,
                                      use_key_padding_mask=use_key_padding_mask)
    token_ids, targets = v03.batch(train_rows, vocab, max_length=MAX_LENGTH)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss = criterion(model(token_ids), targets)
        loss.backward()
        optimizer.step()
    return model


def predict(model: TinyTransformerClassifier, rows: list[dict[str, str]], vocab: dict[str, int]) -> dict[str, str]:
    if not rows:
        return {}
    v03 = load_module(V03, "nlp_v03_for_predict")
    model.eval()
    with torch.inference_mode():
        token_ids, _ = v03.batch(rows, vocab, max_length=MAX_LENGTH)
        predicted = model(token_ids).argmax(dim=1).tolist()
    return {row["sample_id"]: v03.LABELS[index] for row, index in zip(rows, predicted)}


def median_validation_batch_ms(model: TinyTransformerClassifier, rows: list[dict[str, str]],
                               vocab: dict[str, int]) -> float:
    """Small same-batch diagnostic, not a hardware-independent benchmark."""
    v03 = load_module(V03, "nlp_v03_for_timing")
    token_ids, _ = v03.batch(rows, vocab, max_length=MAX_LENGTH)
    model.eval()
    with torch.inference_mode():
        for _ in range(5):
            model(token_ids)
        samples = []
        for _ in range(20):
            started = time.perf_counter()
            model(token_ids)
            samples.append((time.perf_counter() - started) * 1000)
    return round(statistics.median(samples), 4)


def run_validation() -> dict:
    v01 = load_module(V01, "nlp_v01_for_v06")
    v03 = load_module(V03, "nlp_v03_for_vocab")
    rows = v01.read_corpus()
    partitions = v01.split_rows(rows)
    manifest = v01.build_manifest(rows, partitions)
    vocab = v03.build_vocab(partitions["train"])
    variants = {
        "full": (True, True),
        "no_position": (False, True),
        "no_key_padding_mask": (True, False),
    }
    results = {}
    for name, (use_position, use_key_padding_mask) in variants.items():
        started = time.perf_counter()
        model = fit(partitions["train"], vocab, use_position=use_position,
                    use_key_padding_mask=use_key_padding_mask)
        train_seconds = round(time.perf_counter() - started, 4)
        predictions = predict(model, partitions["validation"], vocab)
        errors = [{"sample_id": row["sample_id"], "actual": row["label"],
                   "predicted": predictions[row["sample_id"]]}
                  for row in partitions["validation"] if predictions[row["sample_id"]] != row["label"]]
        results[name] = {
            "use_position": use_position,
            "use_key_padding_mask": use_key_padding_mask,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            "train_seconds": train_seconds,
            "validation_batch_ms_median": median_validation_batch_ms(model, partitions["validation"], vocab),
            "model_validation": v01.evaluate_validation(partitions, predictions),
            "validation_errors": errors,
        }
    return {
        "project_version": "0.6",
        "corpus_sha256": manifest["corpus_sha256"],
        "split_seed": manifest["seed"],
        "train_ids": manifest["partitions"]["train"]["sample_ids"],
        "validation_ids": manifest["partitions"]["validation"]["sample_ids"],
        "train_rows": len(partitions["train"]),
        "validation_rows": len(partitions["validation"]),
        "test_status": "sealed",
        "tokenizer": "latin-words-and-han-characters-v1 (v0.3)",
        "vocab_size": len(vocab),
        "model": "single-layer-transformer-encoder-mean-pool",
        "configuration": {"seed": SEED, "max_length": MAX_LENGTH, "epochs": EPOCHS,
                          "learning_rate": LEARNING_RATE, "width": 16, "heads": 2,
                          "feedforward_width": 32, "dropout": 0.0, "device": "cpu"},
        "variants": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_validation(), ensure_ascii=False, sort_keys=True, indent=2))
