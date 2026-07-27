from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text


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
class TreeResult:
    max_depth_setting: int | None
    actual_depth: int
    node_count: int
    leaf_count: int
    train_accuracy: float
    validation_accuracy: float
    validation_recall: float
    root_feature: str
    root_threshold: float


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
    expected = ("sample_id", *FEATURE_COLUMNS, "target")
    if tuple(frame.columns) != expected or not frame["sample_id"].is_unique:
        raise ValueError("dataset does not match the v0.4 contract")
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


def build_pipeline(max_depth: int | None, min_samples_leaf: int = 1) -> Pipeline:
    if max_depth is not None and max_depth < 1:
        raise ValueError("max_depth must be positive or None")
    if min_samples_leaf < 1:
        raise ValueError("min_samples_leaf must be positive")
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return Pipeline([
        ("preprocess", ColumnTransformer([
            ("numeric", numeric, list(NUMERIC_COLUMNS)),
            ("categorical", categorical, list(CATEGORICAL_COLUMNS)),
        ])),
        ("classifier", DecisionTreeClassifier(
            criterion="gini",
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=SEED,
        )),
    ])


def evaluate(pipeline: Pipeline, split: DatasetSplit) -> TreeResult:
    tree = pipeline.named_steps["classifier"]
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    root_index = int(tree.tree_.feature[0])
    return TreeResult(
        max_depth_setting=tree.max_depth,
        actual_depth=tree.get_depth(),
        node_count=tree.tree_.node_count,
        leaf_count=tree.get_n_leaves(),
        train_accuracy=float(accuracy_score(split.y_train, pipeline.predict(split.x_train))),
        validation_accuracy=float(accuracy_score(split.y_validation, pipeline.predict(split.x_validation))),
        validation_recall=float(recall_score(split.y_validation, pipeline.predict(split.x_validation), zero_division=0)),
        root_feature=str(names[root_index]),
        root_threshold=float(tree.tree_.threshold[0]),
    )


def tree_rules(pipeline: Pipeline) -> str:
    names = list(pipeline.named_steps["preprocess"].get_feature_names_out())
    return export_text(pipeline.named_steps["classifier"], feature_names=names)


def fixed_report() -> str:
    split = split_dataset(build_dataset())
    unconstrained_pipeline = build_pipeline(None).fit(split.x_train, split.y_train)
    constrained_pipeline = build_pipeline(3, min_samples_leaf=5).fit(split.x_train, split.y_train)
    unconstrained = evaluate(unconstrained_pipeline, split)
    constrained = evaluate(constrained_pipeline, split)
    rule_lines = [line for line in tree_rules(constrained_pipeline).splitlines() if line.strip()]
    return "\n".join([
        "model=decision-tree,criterion=gini,seed=20260723",
        f"unconstrained=depth:{unconstrained.actual_depth},nodes:{unconstrained.node_count},leaves:{unconstrained.leaf_count},train_accuracy:{unconstrained.train_accuracy:.3f},validation_accuracy:{unconstrained.validation_accuracy:.3f}",
        f"constrained=max_depth:3,min_samples_leaf:5,depth:{constrained.actual_depth},nodes:{constrained.node_count},leaves:{constrained.leaf_count}",
        f"constrained_metrics=train_accuracy:{constrained.train_accuracy:.3f},validation_accuracy:{constrained.validation_accuracy:.3f},recall:{constrained.validation_recall:.3f}",
        f"root_split={constrained.root_feature}<={constrained.root_threshold:.3f}",
        f"rule_lines={len(rule_lines)}",
        f"capacity_reduced={str(constrained.node_count < unconstrained.node_count).lower()}",
        f"training_gap_unconstrained={unconstrained.train_accuracy - unconstrained.validation_accuracy:.3f}",
        f"training_gap_constrained={constrained.train_accuracy - constrained.validation_accuracy:.3f}",
        "invariants=train-only-fit,fixed-seed,validation-for-comparison",
    ])


if __name__ == "__main__":
    print(fixed_report())
