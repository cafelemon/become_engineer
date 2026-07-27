from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random
from typing import Sequence


@dataclass(frozen=True)
class LabeledSample:
    sample_id: str
    label: int


@dataclass(frozen=True)
class Split:
    training: tuple[LabeledSample, ...]
    validation: tuple[LabeledSample, ...]

    def label_counts(self, partition: str) -> tuple[tuple[int, int], ...]:
        samples = self.training if partition == "training" else self.validation
        return tuple(sorted(Counter(sample.label for sample in samples).items()))


def stratified_split(
    samples: Sequence[LabeledSample],
    *,
    validation_per_label: int,
    seed: int,
) -> Split:
    if validation_per_label <= 0:
        raise ValueError("validation_per_label must be positive")
    if len({sample.sample_id for sample in samples}) != len(samples):
        raise ValueError("sample identifiers must be unique before splitting")
    if any(sample.label not in (0, 1) for sample in samples):
        raise ValueError("labels must be 0 or 1")

    by_label: dict[int, list[LabeledSample]] = {0: [], 1: []}
    for sample in sorted(samples, key=lambda item: item.sample_id):
        by_label[sample.label].append(sample)
    if any(len(group) <= validation_per_label for group in by_label.values()):
        raise ValueError("each label needs training and validation samples")

    rng = Random(seed)
    validation_ids: set[str] = set()
    for label in sorted(by_label):
        candidates = list(by_label[label])
        rng.shuffle(candidates)
        validation_ids.update(sample.sample_id for sample in candidates[:validation_per_label])

    training = tuple(sample for sample in sorted(samples, key=lambda item: item.sample_id)
                     if sample.sample_id not in validation_ids)
    validation = tuple(sample for sample in sorted(samples, key=lambda item: item.sample_id)
                       if sample.sample_id in validation_ids)
    return Split(training, validation)


def _counts_text(counts: tuple[tuple[int, int], ...]) -> str:
    return ",".join(f"{label}:{count}" for label, count in counts)


def fixed_report() -> str:
    samples = tuple(
        LabeledSample(sample_id, label)
        for sample_id, label in (
            ("a", 0), ("b", 0), ("c", 0), ("d", 0),
            ("e", 1), ("f", 1), ("g", 1), ("h", 1),
        )
    )
    seed = 20260723
    split = stratified_split(samples, validation_per_label=1, seed=seed)
    repeated = stratified_split(samples, validation_per_label=1, seed=seed)
    overlap = {sample.sample_id for sample in split.training} & {
        sample.sample_id for sample in split.validation
    }
    return "\n".join([
        f"seed={seed}",
        f"training_ids={','.join(sample.sample_id for sample in split.training)}",
        f"validation_ids={','.join(sample.sample_id for sample in split.validation)}",
        f"training_label_counts={_counts_text(split.label_counts('training'))}",
        f"validation_label_counts={_counts_text(split.label_counts('validation'))}",
        f"overlap={len(overlap)}",
        f"repeated={'identical' if split == repeated else 'changed'}",
        "duplicate_id=reject",
        "invariants=seeded-local-rng,stratified,no-overlap",
    ])


if __name__ == "__main__":
    print(fixed_report())
