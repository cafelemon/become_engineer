"""Train a small, deterministic TF-IDF + linear classifier on v0.1's split."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path

V01 = Path(__file__).resolve().parent.parent / "text-classification-evolution-v01" / "experiment.py"
EPOCHS = 300
LEARNING_RATE = 1.0
L2 = 0.01


def load_v01():
    spec = importlib.util.spec_from_file_location("text_classification_v01", V01)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load v0.1 contract: {V01}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tokens(text: str) -> list[str]:
    """Adjacent character pairs after lowercasing and whitespace removal."""
    compact = "".join(text.lower().split())
    return [compact[i:i + 2] for i in range(len(compact) - 1)]


def fit_vectorizer(texts: list[str]) -> dict[str, float]:
    """Learn a vocabulary and smoothed IDF from training texts only."""
    if not texts:
        raise ValueError("training texts cannot be empty")
    document_frequency = Counter(token for text in texts for token in set(tokens(text)))
    return {token: 1.0 + math.log((1 + len(texts)) / (1 + count))
            for token, count in sorted(document_frequency.items())}


def transform(text: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(token for token in tokens(text) if token in idf)
    weights = {token: count * idf[token] for token, count in counts.items()}
    norm = math.sqrt(sum(value * value for value in weights.values()))
    return {token: value / norm for token, value in weights.items()} if norm else {}


def train_linear(rows: list[dict[str, str]], idf: dict[str, float],
                 epochs: int = EPOCHS, learning_rate: float = LEARNING_RATE,
                 l2: float = L2) -> tuple[dict[str, float], float]:
    """Full-batch binary logistic regression; positive class is code."""
    if not rows or epochs < 1 or learning_rate <= 0 or l2 < 0:
        raise ValueError("invalid training configuration")
    examples = [(transform(row["text"], idf), int(row["label"] == "code")) for row in rows]
    weights = {token: 0.0 for token in idf}
    bias = 0.0
    for _ in range(epochs):
        gradient = {token: l2 * weights[token] for token in idf}
        bias_gradient = 0.0
        for vector, label in examples:
            score = bias + sum(weights[token] * value for token, value in vector.items())
            probability = 1 / (1 + math.exp(-score))
            error = (probability - label) / len(examples)
            bias_gradient += error
            for token, value in vector.items():
                gradient[token] += error * value
        for token in weights:
            weights[token] -= learning_rate * gradient[token]
        bias -= learning_rate * bias_gradient
    return weights, bias


def predict(text: str, idf: dict[str, float], weights: dict[str, float], bias: float) -> str:
    vector = transform(text, idf)
    score = bias + sum(weights[token] * value for token, value in vector.items())
    return "code" if score >= 0 else "plan"


def run() -> dict:
    v01 = load_v01()
    rows = v01.read_corpus()
    partitions = v01.split_rows(rows)
    manifest = v01.build_manifest(rows, partitions)
    train = partitions["train"]
    validation = partitions["validation"]
    idf = fit_vectorizer([row["text"] for row in train])
    weights, bias = train_linear(train, idf)
    majority = sorted(Counter(row["label"] for row in train).items(), key=lambda item: (-item[1], item[0]))[0][0]
    baseline_predictions = {row["sample_id"]: majority for row in validation}
    model_predictions = {row["sample_id"]: predict(row["text"], idf, weights, bias) for row in validation}
    baseline = v01.evaluate_validation(partitions, baseline_predictions)
    model = v01.evaluate_validation(partitions, model_predictions)
    errors = [{"sample_id": row["sample_id"], "text": row["text"],
               "actual": row["label"], "predicted": model_predictions[row["sample_id"]]}
              for row in validation if model_predictions[row["sample_id"]] != row["label"]]
    return {"version": "0.2", "corpus_sha256": manifest["corpus_sha256"],
            "split_seed": manifest["seed"], "train_ids": manifest["partitions"]["train"]["sample_ids"],
            "validation_ids": manifest["partitions"]["validation"]["sample_ids"],
            "test_policy": "sealed; not transformed, predicted, or evaluated",
            "configuration": {"tokenizer": "character_bigram_lowercase_no_whitespace",
                              "tf": "raw_count", "idf": "1+ln((1+n)/(1+df))", "norm": "l2",
                              "classifier": "batch_logistic_regression", "epochs": EPOCHS,
                              "learning_rate": LEARNING_RATE, "l2": L2},
            "vocabulary_size": len(idf), "majority_label": majority,
            "baseline_validation": baseline, "model_validation": model,
            "validation_errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write result.json in a new or empty directory")
    args = parser.parse_args()
    result = run()
    if args.output:
        if args.output.exists() and any(args.output.iterdir()):
            raise FileExistsError(f"output directory is not empty: {args.output}")
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"vocabulary_size={result['vocabulary_size']}")
    for name in ("baseline_validation", "model_validation"):
        metrics = result[name]
        print(f"{name}: accuracy={metrics['accuracy']:.3f},macro_f1={metrics['macro_f1']:.3f}")
    print("validation_errors=" + ",".join(item["sample_id"] for item in result["validation_errors"]))
    print("test_policy=sealed")


if __name__ == "__main__":
    main()
