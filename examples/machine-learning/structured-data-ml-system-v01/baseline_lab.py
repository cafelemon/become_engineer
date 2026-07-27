from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split


SEED = 20260723
FEATURE_COLUMNS = ("signal_a", "signal_b", "noise", "redundant_signal")
EXPECTED_COLUMNS = ("sample_id", *FEATURE_COLUMNS, "target")


@dataclass(frozen=True)
class DatasetSplit:
    x_train: pd.DataFrame
    x_validation: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    train_ids: pd.Series
    validation_ids: pd.Series


@dataclass(frozen=True)
class BaselineResult:
    strategy: str
    predicted_label: int
    accuracy: float
    recall: float


def build_dataset(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    target = np.concatenate((np.zeros(80, dtype=np.int64), np.ones(40, dtype=np.int64)))
    signal_a = target * 1.5 + rng.normal(0, 1, target.size)
    signal_b = target * 0.8 + rng.normal(0, 1, target.size)
    noise = rng.normal(0, 1, target.size)
    redundant_signal = signal_a * 0.5 + rng.normal(0, 0.2, target.size)
    order = rng.permutation(target.size)
    return pd.DataFrame({
        "sample_id": pd.Series([f"sample-{index:03d}" for index in range(target.size)], dtype="string").iloc[order].reset_index(drop=True),
        "signal_a": signal_a[order],
        "signal_b": signal_b[order],
        "noise": noise[order],
        "redundant_signal": redundant_signal[order],
        "target": target[order],
    })


def validate_dataset(frame: pd.DataFrame) -> None:
    if tuple(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError("dataset columns or order do not match the contract")
    if frame.empty or frame["sample_id"].isna().any() or not frame["sample_id"].is_unique:
        raise ValueError("sample_id must be non-empty and unique")
    if frame[list(FEATURE_COLUMNS)].isna().any().any():
        raise ValueError("v0.1 baseline does not accept missing features")
    if not all(pd.api.types.is_numeric_dtype(frame[column]) for column in FEATURE_COLUMNS):
        raise ValueError("all v0.1 features must be numeric")
    if set(frame["target"].unique()) != {0, 1}:
        raise ValueError("target must contain binary labels 0 and 1")


def split_dataset(frame: pd.DataFrame, seed: int = SEED) -> DatasetSplit:
    validate_dataset(frame)
    features = frame.loc[:, FEATURE_COLUMNS]
    target = frame["target"]
    sample_ids = frame["sample_id"]
    x_train, x_validation, y_train, y_validation, train_ids, validation_ids = train_test_split(
        features,
        target,
        sample_ids,
        test_size=0.25,
        random_state=seed,
        stratify=target,
    )
    return DatasetSplit(
        x_train.reset_index(drop=True),
        x_validation.reset_index(drop=True),
        y_train.reset_index(drop=True),
        y_validation.reset_index(drop=True),
        train_ids.reset_index(drop=True),
        validation_ids.reset_index(drop=True),
    )


def evaluate_most_frequent_baseline(split: DatasetSplit) -> BaselineResult:
    model = DummyClassifier(strategy="most_frequent")
    model.fit(split.x_train, split.y_train)
    predictions = model.predict(split.x_validation)
    return BaselineResult(
        strategy="most_frequent",
        predicted_label=int(model.classes_[np.argmax(model.class_prior_)]),
        accuracy=float(accuracy_score(split.y_validation, predictions)),
        recall=float(recall_score(split.y_validation, predictions, zero_division=0)),
    )


def _counts(series: pd.Series) -> str:
    return ",".join(f"{int(label)}:{int(count)}" for label, count in series.value_counts().sort_index().items())


def fixed_report() -> str:
    frame = build_dataset()
    split = split_dataset(frame)
    baseline = evaluate_most_frequent_baseline(split)
    overlap = set(split.train_ids) & set(split.validation_ids)
    return "\n".join([
        f"rows={len(frame)}",
        f"features={len(FEATURE_COLUMNS)}",
        "target=target,binary=0|1,positive=1",
        f"target_rate={frame['target'].mean():.3f}",
        f"train_rows={len(split.x_train)},class_counts={_counts(split.y_train)}",
        f"validation_rows={len(split.x_validation)},class_counts={_counts(split.y_validation)}",
        f"overlap={len(overlap)}",
        f"baseline_strategy={baseline.strategy},predicted_label={baseline.predicted_label}",
        f"baseline_accuracy={baseline.accuracy:.3f}",
        f"baseline_recall={baseline.recall:.3f}",
        "invariants=target-excluded,stratified-split,validation-untouched",
    ])


if __name__ == "__main__":
    print(fixed_report())
