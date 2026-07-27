from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


SEED = 20260723
NUMERIC_COLUMNS = ("signal_a", "signal_b", "noise", "redundant_signal")
CATEGORICAL_COLUMNS = ("channel",)
FEATURE_COLUMNS = (*NUMERIC_COLUMNS, *CATEGORICAL_COLUMNS)


@dataclass(frozen=True)
class HoldoutSplit:
    x_development: pd.DataFrame
    x_test: pd.DataFrame
    y_development: pd.Series
    y_test: pd.Series
    development_ids: pd.Series
    test_ids: pd.Series


@dataclass(frozen=True)
class SelectionResult:
    search: GridSearchCV
    best_family: str
    best_parameter: str
    cv_balanced_accuracy: float
    cv_standard_deviation: float
    test_accuracy: float
    test_balanced_accuracy: float
    test_recall: float


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


def make_holdout(frame: pd.DataFrame, seed: int = SEED) -> HoldoutSplit:
    expected = ("sample_id", *FEATURE_COLUMNS, "target")
    if tuple(frame.columns) != expected or not frame["sample_id"].is_unique:
        raise ValueError("dataset does not match the v0.5 contract")
    values = train_test_split(
        frame.loc[:, FEATURE_COLUMNS],
        frame["target"],
        frame["sample_id"],
        test_size=0.25,
        random_state=seed,
        stratify=frame["target"],
    )
    x_development, x_test, y_development, y_test, development_ids, test_ids = values
    return HoldoutSplit(
        x_development.reset_index(drop=True),
        x_test.reset_index(drop=True),
        y_development.reset_index(drop=True),
        y_test.reset_index(drop=True),
        development_ids.reset_index(drop=True),
        test_ids.reset_index(drop=True),
    )


def build_search() -> GridSearchCV:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    pipeline = Pipeline([
        ("preprocess", ColumnTransformer([
            ("numeric", numeric, list(NUMERIC_COLUMNS)),
            ("categorical", categorical, list(CATEGORICAL_COLUMNS)),
        ])),
        ("classifier", LogisticRegression(l1_ratio=0, solver="lbfgs", max_iter=1000, random_state=SEED)),
    ])
    grids = [
        {
            "classifier": [LogisticRegression(l1_ratio=0, solver="lbfgs", max_iter=1000, random_state=SEED)],
            "classifier__C": [0.1, 1.0, 10.0],
        },
        {
            "classifier": [DecisionTreeClassifier(min_samples_leaf=5, random_state=SEED)],
            "classifier__max_depth": [2, 3, 4],
        },
    ]
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    return GridSearchCV(
        estimator=pipeline,
        param_grid=grids,
        scoring="balanced_accuracy",
        cv=folds,
        refit=True,
        return_train_score=True,
        n_jobs=1,
        error_score="raise",
    )


def _selection_name(search: GridSearchCV) -> tuple[str, str]:
    classifier = search.best_estimator_.named_steps["classifier"]
    if isinstance(classifier, LogisticRegression):
        return "logistic-regression", f"C={classifier.C:g}"
    if isinstance(classifier, DecisionTreeClassifier):
        return "decision-tree", f"max_depth={classifier.max_depth}"
    raise TypeError("unsupported selected classifier")


def run_selection(split: HoldoutSplit) -> SelectionResult:
    search = build_search()
    search.fit(split.x_development, split.y_development)
    family, parameter = _selection_name(search)
    best_index = int(search.best_index_)
    predictions = search.predict(split.x_test)
    return SelectionResult(
        search=search,
        best_family=family,
        best_parameter=parameter,
        cv_balanced_accuracy=float(search.cv_results_["mean_test_score"][best_index]),
        cv_standard_deviation=float(search.cv_results_["std_test_score"][best_index]),
        test_accuracy=float(accuracy_score(split.y_test, predictions)),
        test_balanced_accuracy=float(balanced_accuracy_score(split.y_test, predictions)),
        test_recall=float(recall_score(split.y_test, predictions, zero_division=0)),
    )


def fixed_report() -> str:
    split = make_holdout(build_dataset())
    result = run_selection(split)
    overlap = set(split.development_ids) & set(split.test_ids)
    return "\n".join([
        f"rows=120,development_rows={len(split.x_development)},test_rows={len(split.x_test)},overlap={len(overlap)}",
        "selection_scope=development-only,cv=stratified-5-fold,scoring=balanced_accuracy",
        "candidates=logistic-regression:C[0.1|1|10];decision-tree:max_depth[2|3|4],min_samples_leaf:5",
        "candidate_count=6,fit_count=30",
        f"selected={result.best_family},{result.best_parameter}",
        f"cv_balanced_accuracy={result.cv_balanced_accuracy:.3f},std={result.cv_standard_deviation:.3f}",
        f"final_test=accuracy:{result.test_accuracy:.3f},balanced_accuracy:{result.test_balanced_accuracy:.3f},recall:{result.test_recall:.3f}",
        "test_access=after-selection-once",
        "invariants=preprocess-inside-cv,test-excluded-from-selection,refit-development-only",
    ])


if __name__ == "__main__":
    print(fixed_report())
