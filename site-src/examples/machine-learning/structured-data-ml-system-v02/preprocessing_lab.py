from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


SEED = 20260723
NUMERIC_COLUMNS = ("signal_a", "signal_b", "noise", "redundant_signal")
CATEGORICAL_COLUMNS = ("channel",)
FEATURE_COLUMNS = (*NUMERIC_COLUMNS, *CATEGORICAL_COLUMNS)
EXPECTED_COLUMNS = ("sample_id", *FEATURE_COLUMNS, "target")


@dataclass(frozen=True)
class DatasetSplit:
    x_train: pd.DataFrame
    x_validation: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    train_ids: pd.Series
    validation_ids: pd.Series


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


def validate_dataset(frame: pd.DataFrame) -> None:
    if tuple(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError("dataset columns or order do not match the contract")
    if frame.empty or frame["sample_id"].isna().any() or not frame["sample_id"].is_unique:
        raise ValueError("sample_id must be non-empty and unique")
    if not all(pd.api.types.is_numeric_dtype(frame[column]) for column in NUMERIC_COLUMNS):
        raise ValueError("numeric feature columns must remain numeric")
    if any(frame[column].notna().sum() == 0 for column in FEATURE_COLUMNS):
        raise ValueError("no feature column may be entirely missing")
    if set(frame["target"].unique()) != {0, 1}:
        raise ValueError("target must contain binary labels 0 and 1")


def split_dataset(frame: pd.DataFrame, seed: int = SEED) -> DatasetSplit:
    validate_dataset(frame)
    x_train, x_validation, y_train, y_validation, train_ids, validation_ids = train_test_split(
        frame.loc[:, FEATURE_COLUMNS],
        frame["target"],
        frame["sample_id"],
        test_size=0.25,
        random_state=seed,
        stratify=frame["target"],
    )
    return DatasetSplit(
        x_train.reset_index(drop=True),
        x_validation.reset_index(drop=True),
        y_train.reset_index(drop=True),
        y_validation.reset_index(drop=True),
        train_ids.reset_index(drop=True),
        validation_ids.reset_index(drop=True),
    )


def build_pipeline() -> Pipeline:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric, list(NUMERIC_COLUMNS)),
        ("categorical", categorical, list(CATEGORICAL_COLUMNS)),
    ])
    return Pipeline([
        ("preprocess", preprocessor),
        ("classifier", DummyClassifier(strategy="most_frequent")),
    ])


def transformed_feature_names(pipeline: Pipeline) -> tuple[str, ...]:
    preprocessor = pipeline.named_steps["preprocess"]
    return tuple(str(name) for name in preprocessor.get_feature_names_out())


def fixed_report() -> str:
    frame = build_dataset()
    split = split_dataset(frame)
    raw_validation = split.x_validation.copy(deep=True)
    pipeline = build_pipeline()
    pipeline.fit(split.x_train, split.y_train)
    predictions = pipeline.predict(split.x_validation)
    transformed = pipeline.named_steps["preprocess"].transform(split.x_validation)
    numeric_imputer = pipeline.named_steps["preprocess"].named_transformers_["numeric"].named_steps["imputer"]
    names = transformed_feature_names(pipeline)
    pd.testing.assert_frame_equal(split.x_validation, raw_validation)
    return "\n".join([
        f"rows={len(frame)},raw_features={len(FEATURE_COLUMNS)}",
        f"missing=signal_a:{int(frame['signal_a'].isna().sum())},signal_b:{int(frame['signal_b'].isna().sum())},channel:{int(frame['channel'].isna().sum())}",
        f"train_rows={len(split.x_train)},validation_rows={len(split.x_validation)}",
        f"fit_scope=train-only,train_median_signal_a={numeric_imputer.statistics_[0]:.3f}",
        f"transformed_features={len(names)},validation_shape={transformed.shape[0]}x{transformed.shape[1]}",
        f"feature_names={','.join(names)}",
        f"post_transform_missing={int(np.isnan(transformed).sum())}",
        f"unknown_category=ignored,raw_validation_unchanged={str(split.x_validation.equals(raw_validation)).lower()}",
        f"baseline_accuracy={accuracy_score(split.y_validation, predictions):.3f}",
        "invariants=target-excluded,fit-train-only,same-pipeline-for-validation",
    ])


if __name__ == "__main__":
    print(fixed_report())
