from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


SEED = 20260723
THRESHOLD = 0.35
NUMERIC_COLUMNS = ("signal_a", "signal_b", "noise", "redundant_signal")
CATEGORICAL_COLUMNS = ("channel",)
FEATURE_COLUMNS = (*NUMERIC_COLUMNS, *CATEGORICAL_COLUMNS)


@dataclass(frozen=True)
class HoldoutSplit:
    x_development: pd.DataFrame
    x_test: pd.DataFrame
    y_development: pd.Series
    y_test: pd.Series
    test_ids: pd.Series


@dataclass(frozen=True)
class ProbabilityMetrics:
    brier: float
    log_loss: float
    expected_calibration_error: float


@dataclass(frozen=True)
class GroupMetrics:
    group: str
    samples: int
    positives: int
    recall: float | None
    false_positive_rate: float | None


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
        raise ValueError("dataset does not match the v0.7 contract")
    x_development, x_test, y_development, y_test, _, test_ids = train_test_split(
        frame.loc[:, FEATURE_COLUMNS],
        frame["target"],
        frame["sample_id"],
        test_size=0.25,
        random_state=seed,
        stratify=frame["target"],
    )
    return HoldoutSplit(
        x_development.reset_index(drop=True),
        x_test.reset_index(drop=True),
        y_development.reset_index(drop=True),
        y_test.reset_index(drop=True),
        test_ids.reset_index(drop=True),
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
    return Pipeline([
        ("preprocess", ColumnTransformer([
            ("numeric", numeric, list(NUMERIC_COLUMNS)),
            ("categorical", categorical, list(CATEGORICAL_COLUMNS)),
        ])),
        ("classifier", LogisticRegression(C=1.0, l1_ratio=0, solver="lbfgs", max_iter=1000, random_state=SEED)),
    ])


def expected_calibration_error(y_true: pd.Series | np.ndarray, probabilities: np.ndarray, bins: int = 5) -> float:
    if bins < 2:
        raise ValueError("bins must be at least 2")
    truth = np.asarray(y_true, dtype=np.int64)
    probabilities = np.asarray(probabilities, dtype=float)
    if truth.shape != probabilities.shape or np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("truth and probabilities must align and probabilities must be bounded")
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.minimum(np.digitize(probabilities, edges[1:-1], right=False), bins - 1)
    total = len(truth)
    error = 0.0
    for index in range(bins):
        mask = assignments == index
        if mask.any():
            error += float(mask.sum()) / total * abs(float(probabilities[mask].mean()) - float(truth[mask].mean()))
    return error


def probability_metrics(y_true: pd.Series, probabilities: np.ndarray) -> ProbabilityMetrics:
    return ProbabilityMetrics(
        brier=float(brier_score_loss(y_true, probabilities)),
        log_loss=float(log_loss(y_true, probabilities, labels=[0, 1])),
        expected_calibration_error=expected_calibration_error(y_true, probabilities),
    )


def group_error_table(
    x_test: pd.DataFrame,
    y_test: pd.Series,
    probabilities: np.ndarray,
    threshold: float = THRESHOLD,
) -> tuple[GroupMetrics, ...]:
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1")
    predictions = probabilities >= threshold
    groups = x_test["channel"].fillna("missing").astype(str).reset_index(drop=True)
    truth = y_test.reset_index(drop=True).to_numpy()
    rows: list[GroupMetrics] = []
    for group in sorted(groups.unique()):
        mask = groups.to_numpy() == group
        group_truth = truth[mask]
        group_predictions = predictions[mask]
        positives = int((group_truth == 1).sum())
        negatives = int((group_truth == 0).sum())
        true_positives = int(((group_truth == 1) & group_predictions).sum())
        false_positives = int(((group_truth == 0) & group_predictions).sum())
        rows.append(GroupMetrics(
            group=group,
            samples=int(mask.sum()),
            positives=positives,
            recall=true_positives / positives if positives else None,
            false_positive_rate=false_positives / negatives if negatives else None,
        ))
    return tuple(rows)


def fixed_report() -> str:
    split = make_holdout(build_dataset())
    raw = build_pipeline().fit(split.x_development, split.y_development)
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    calibrated = CalibratedClassifierCV(estimator=build_pipeline(), method="sigmoid", cv=folds)
    calibrated.fit(split.x_development, split.y_development)
    raw_probabilities = raw.predict_proba(split.x_test)[:, 1]
    calibrated_probabilities = calibrated.predict_proba(split.x_test)[:, 1]
    raw_metrics = probability_metrics(split.y_test, raw_probabilities)
    calibrated_metrics = probability_metrics(split.y_test, calibrated_probabilities)
    groups = group_error_table(split.x_test, split.y_test, calibrated_probabilities)
    group_text = ";".join(
        f"{row.group}:n={row.samples},pos={row.positives},recall={'na' if row.recall is None else f'{row.recall:.3f}'},fpr={'na' if row.false_positive_rate is None else f'{row.false_positive_rate:.3f}'}"
        for row in groups
    )
    return "\n".join([
        "model=logistic-regression,calibration=sigmoid,cv=stratified-5-fold",
        f"development_rows={len(split.x_development)},test_rows={len(split.x_test)},test_access=single-analysis",
        f"raw_probability=brier:{raw_metrics.brier:.3f},log_loss:{raw_metrics.log_loss:.3f},ece5:{raw_metrics.expected_calibration_error:.3f}",
        f"calibrated_probability=brier:{calibrated_metrics.brier:.3f},log_loss:{calibrated_metrics.log_loss:.3f},ece5:{calibrated_metrics.expected_calibration_error:.3f}",
        f"decision_threshold={THRESHOLD:.2f},policy=recall-oriented-predeclared",
        f"group_errors={group_text}",
        f"minimum_group_samples={min(row.samples for row in groups)},small_groups_descriptive_only=true",
        "comparison=report-all-metrics-no-cherry-picking",
        "invariants=calibration-development-only,threshold-predeclared,test-not-retuned",
    ])


if __name__ == "__main__":
    print(fixed_report())
