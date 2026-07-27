from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ScoredSample:
    sample_id: str
    actual: int
    score: float


@dataclass(frozen=True)
class Confusion:
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def total(self) -> int:
        return self.true_positive + self.false_positive + self.true_negative + self.false_negative

    def accuracy(self) -> float:
        return _ratio(self.true_positive + self.true_negative, self.total)

    def precision(self) -> float:
        return _ratio(self.true_positive, self.true_positive + self.false_positive)

    def recall(self) -> float:
        return _ratio(self.true_positive, self.true_positive + self.false_negative)

    def f1(self) -> float:
        precision, recall = self.precision(), self.recall()
        return _ratio(2 * precision * recall, precision + recall)


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def confusion_at_threshold(samples: Sequence[ScoredSample], threshold: float) -> Confusion:
    if not samples:
        raise ValueError("evaluation samples must not be empty")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    if len({sample.sample_id for sample in samples}) != len(samples):
        raise ValueError("sample identifiers must be unique")
    if any(sample.actual not in (0, 1) or not 0 <= sample.score <= 1 for sample in samples):
        raise ValueError("actual must be binary and score must be within [0, 1]")

    tp = fp = tn = fn = 0
    for sample in samples:
        predicted = int(sample.score >= threshold)
        if sample.actual == 1 and predicted == 1:
            tp += 1
        elif sample.actual == 0 and predicted == 1:
            fp += 1
        elif sample.actual == 0:
            tn += 1
        else:
            fn += 1
    return Confusion(tp, fp, tn, fn)


def negative_baseline(samples: Sequence[ScoredSample]) -> Confusion:
    if not samples:
        raise ValueError("evaluation samples must not be empty")
    positives = sum(sample.actual == 1 for sample in samples)
    return Confusion(0, 0, len(samples) - positives, positives)


def _summary(name: str, confusion: Confusion) -> str:
    return (
        f"{name}=tp:{confusion.true_positive},fp:{confusion.false_positive},"
        f"tn:{confusion.true_negative},fn:{confusion.false_negative},"
        f"accuracy:{confusion.accuracy():.3f},precision:{confusion.precision():.3f},"
        f"recall:{confusion.recall():.3f},f1:{confusion.f1():.3f}"
    )


def fixed_report() -> str:
    samples = (
        ScoredSample("a", 1, 0.9),
        ScoredSample("b", 1, 0.6),
        ScoredSample("c", 1, 0.4),
        ScoredSample("d", 0, 0.8),
        ScoredSample("e", 0, 0.3),
        ScoredSample("f", 0, 0.1),
    )
    return "\n".join([
        "samples=6,positive=3,negative=3",
        _summary("baseline_negative", negative_baseline(samples)),
        _summary("threshold_0.5", confusion_at_threshold(samples, 0.5)),
        _summary("threshold_0.7", confusion_at_threshold(samples, 0.7)),
        "selection=cost-and-validation-contract",
        "invariants=fixed-validation,threshold-declared,zero-division-defined",
    ])


if __name__ == "__main__":
    print(fixed_report())
