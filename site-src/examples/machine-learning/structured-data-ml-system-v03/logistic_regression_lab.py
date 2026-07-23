from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


SEED = 20260723
NUMERIC_COLUMNS = ("signal_a", "signal_b", "noise", "redundant_signal")
CATEGORICAL_COLUMNS = ("channel",)
FEATURE_COLUMNS = (*NUMERIC_COLUMNS, *CATEGORICAL_COLUMNS)


@dataclass(frozen=True)
class DatasetSplit:
    x_train: pd.DataFrame
    x_validation: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series


@dataclass(frozen=True)
class ModelResult:
    c: float
    accuracy: float
    recall: float
    loss: float
    coefficient_l2: float
    intercept: float
    minimum_probability: float
    maximum_probability: float


def build_dataset(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    target = np.concatenate((np.zeros(80, dtype=np.int64), np.ones(40, dtype=np.int64)))
    signal_a = target * 1.5 + rng.normal(0, 1, target.size)
    signal_b = target * 0.8 + rng.normal(0, 1, target.size)
    noise = rng.normal(0, 1, target.size)
    redundant_signal = signal_a * 0.5 + rng.normal(0, 0.2, target.size)
    channel = np.resize(np.array(["direct", "organic", "referral"], dtype=object), target.size)
    order = rng.permutation(target.size)
    frame = pd.DataFrame({
        "sample_id": pd.Series([f"sample-{index:03d}" for index in range(target.size)], dtype="string").iloc[order].reset_index(drop=True),
        "signal_a": signal_a[order],
        "signal_b": signal_b[order],
        "noise": noise[order],
        "redundant_signal": redundant_signal[order],
        "channel": pd.Series(channel[order], dtype="object"),
        "target": target[order],
    })
    frame.loc[frame.index % 11 == 0, "signal_a"] = np.nan
    frame.loc[frame.index % 17 == 0, "signal_b"] = np.nan
    frame.loc[frame.index % 19 == 0, "channel"] = np.nan
    return frame


def split_dataset(frame: pd.DataFrame, seed: int = SEED) -> DatasetSplit:
    if tuple(frame.columns) != ("sample_id", *FEATURE_COLUMNS, "target"):
        raise ValueError("dataset columns do not match the v0.3 contract")
    if not frame["sample_id"].is_unique or set(frame["target"].unique()) != {0, 1}:
        raise ValueError("sample IDs must be unique and target must be binary")
    x_train, x_validation, y_train, y_validation = train_test_split(
        frame.loc[:, FEATURE_COLUMNS],
        frame["target"],
        test_size=0.25,
        random_state=seed,
        stratify=frame["target"],
    )
    return DatasetSplit(
        x_train.reset_index(drop=True),
        x_validation.reset_index(drop=True),
        y_train.reset_index(drop=True),
        y_validation.reset_index(drop=True),
    )


def build_pipeline(c: float = 1.0) -> Pipeline:
    if c <= 0:
        raise ValueError("C must be positive")
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return Pipeline([
        ("preprocess", ColumnTransformer([
            ("numeric", numeric, list(NUMERIC_COLUMNS)),
            ("categorical", categorical, list(CATEGORICAL_COLUMNS)),
        ])),
        ("classifier", LogisticRegression(C=c, l1_ratio=0, solver="lbfgs", max_iter=1000, random_state=SEED)),
    ])


def evaluate(pipeline: Pipeline, split: DatasetSplit) -> ModelResult:
    probabilities = pipeline.predict_proba(split.x_validation)[:, 1]
    predictions = (probabilities >= 0.5).astype(np.int64)
    classifier = pipeline.named_steps["classifier"]
    return ModelResult(
        c=float(classifier.C),
        accuracy=float(accuracy_score(split.y_validation, predictions)),
        recall=float(recall_score(split.y_validation, predictions, zero_division=0)),
        loss=float(log_loss(split.y_validation, probabilities, labels=[0, 1])),
        coefficient_l2=float(np.linalg.norm(classifier.coef_)),
        intercept=float(classifier.intercept_[0]),
        minimum_probability=float(probabilities.min()),
        maximum_probability=float(probabilities.max()),
    )


def fit_and_evaluate(c: float = 1.0) -> tuple[Pipeline, ModelResult]:
    split = split_dataset(build_dataset())
    pipeline = build_pipeline(c)
    pipeline.fit(split.x_train, split.y_train)
    return pipeline, evaluate(pipeline, split)


def fixed_report() -> str:
    split = split_dataset(build_dataset())
    pipeline = build_pipeline(1.0).fit(split.x_train, split.y_train)
    result = evaluate(pipeline, split)
    strong_regularization = build_pipeline(0.1).fit(split.x_train, split.y_train)
    weak_regularization = build_pipeline(10.0).fit(split.x_train, split.y_train)
    strong = evaluate(strong_regularization, split)
    weak = evaluate(weak_regularization, split)
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    coefficients = pipeline.named_steps["classifier"].coef_[0]
    strongest_index = int(np.argmax(np.abs(coefficients)))
    return "\n".join([
        "model=logistic-regression,penalty=l2,solver=lbfgs,threshold=0.500",
        f"train_rows={len(split.x_train)},validation_rows={len(split.x_validation)},transformed_features={len(names)}",
        f"validation_accuracy={result.accuracy:.3f},recall={result.recall:.3f},log_loss={result.loss:.3f}",
        f"probability_range={result.minimum_probability:.3f}..{result.maximum_probability:.3f}",
        f"intercept={result.intercept:.3f},coefficient_l2={result.coefficient_l2:.3f}",
        f"strongest_absolute_coefficient={names[strongest_index]}:{coefficients[strongest_index]:.3f}",
        f"regularization=C:0.1,l2:{strong.coefficient_l2:.3f};C:10.0,l2:{weak.coefficient_l2:.3f}",
        f"weaker_regularization_larger_norm={str(weak.coefficient_l2 > strong.coefficient_l2).lower()}",
        "invariants=train-only-preprocessing,probabilities-not-decisions,validation-not-fit",
    ])


if __name__ == "__main__":
    print(fixed_report())
