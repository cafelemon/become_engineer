"""Freeze a small, offline text-classification task before fitting a model."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SEED = "be-nlp-v01-20261013"
LABELS = ("code", "plan")
SPLIT_COUNTS = {"train": 12, "validation": 4, "test": 4}  # Per label.
CORPUS = Path(__file__).with_name("corpus.csv")


def read_corpus(path: Path = CORPUS) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["sample_id", "label", "text"]:
            raise ValueError("corpus schema must be sample_id,label,text")
        rows = list(reader)
    if len(rows) != 40:
        raise ValueError("v0.1 corpus must contain exactly 40 rows")
    ids: set[str] = set()
    normalized_texts: set[str] = set()
    labels = Counter()
    for row in rows:
        if not re.fullmatch(r"[CP]\d{2}", row["sample_id"]):
            raise ValueError("invalid sample_id")
        if row["sample_id"] in ids:
            raise ValueError("duplicate sample_id")
        ids.add(row["sample_id"])
        if row["label"] not in LABELS:
            raise ValueError("unknown label")
        labels[row["label"]] += 1
        normalized = "".join(row["text"].lower().split())
        if not normalized or normalized in normalized_texts:
            raise ValueError("blank or duplicate text")
        normalized_texts.add(normalized)
    if labels != Counter({"code": 20, "plan": 20}):
        raise ValueError("v0.1 requires 20 rows per label")
    return rows


def corpus_sha256(rows: list[dict[str, str]]) -> str:
    canonical = json.dumps(sorted(rows, key=lambda row: row["sample_id"]), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def split_rows(rows: list[dict[str, str]], seed: str = SEED) -> dict[str, list[dict[str, str]]]:
    """Assign stable disjoint IDs, stratified by label; input order is irrelevant."""
    result: dict[str, list[dict[str, str]]] = {name: [] for name in SPLIT_COUNTS}
    for label in LABELS:
        same_label = [row for row in rows if row["label"] == label]
        same_label.sort(key=lambda row: (hashlib.sha256(f"{seed}:{row['sample_id']}".encode()).hexdigest(), row["sample_id"]))
        offset = 0
        for name, count in SPLIT_COUNTS.items():
            result[name].extend(same_label[offset:offset + count])
            offset += count
    for partition in result.values():
        partition.sort(key=lambda row: row["sample_id"])
    ids = [row["sample_id"] for partition in result.values() for row in partition]
    if len(ids) != len(set(ids)) or len(ids) != len(rows):
        raise ValueError("split must cover each sample exactly once")
    return result


def build_manifest(rows: list[dict[str, str]], partitions: dict[str, list[dict[str, str]]]) -> dict:
    return {
        "version": "0.1",
        "task": "learning-question-category",
        "labels": list(LABELS),
        "seed": SEED,
        "corpus_sha256": corpus_sha256(rows),
        "split_counts_per_label": SPLIT_COUNTS,
        "partitions": {
            name: {"sample_ids": [row["sample_id"] for row in partition], "class_counts": dict(sorted(Counter(row["label"] for row in partition).items()))}
            for name, partition in partitions.items()
        },
        "policy": "fit on train only; compare on validation; keep test sealed until final model selection",
    }


def evaluate_validation(partitions: dict[str, list[dict[str, str]]], predictions: dict[str, str]) -> dict:
    """Score one complete validation prediction set; never inspect test labels."""
    expected = {row["sample_id"]: row["label"] for row in partitions["validation"]}
    if set(predictions) != set(expected):
        raise ValueError("prediction IDs must exactly match validation IDs")
    if set(predictions.values()) - set(LABELS):
        raise ValueError("prediction contains an unknown label")
    confusion = {actual: {predicted: 0 for predicted in LABELS} for actual in LABELS}
    for sample_id, actual in expected.items():
        confusion[actual][predictions[sample_id]] += 1
    correct = sum(confusion[label][label] for label in LABELS)
    f1s = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[actual][label] for actual in LABELS if actual != label)
        fn = sum(confusion[label][predicted] for predicted in LABELS if predicted != label)
        denominator = 2 * tp + fp + fn
        f1s.append(0.0 if denominator == 0 else 2 * tp / denominator)
    return {"accuracy": correct / len(expected), "macro_f1": sum(f1s) / len(f1s), "confusion": confusion}


def write_artifacts(output: Path, partitions: dict[str, list[dict[str, str]]], manifest: dict) -> None:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    for name, partition in partitions.items():
        with (output / f"{name}.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["sample_id", "label", "text"])
            writer.writeheader()
            writer.writerows(partition)
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write split CSVs and manifest into an empty directory")
    args = parser.parse_args()
    rows = read_corpus()
    partitions = split_rows(rows)
    manifest = build_manifest(rows, partitions)
    if args.output:
        write_artifacts(args.output, partitions, manifest)
    print(f"rows={len(rows)},labels=code:20,plan:20")
    for name, partition in partitions.items():
        counts = Counter(row["label"] for row in partition)
        print(f"{name}_rows={len(partition)},class_counts=code:{counts['code']},plan:{counts['plan']}")
    print("overlap=0")
    print(f"corpus_sha256={manifest['corpus_sha256']}")
    print("test_policy=sealed_until_final_selection")


if __name__ == "__main__":
    main()
