from __future__ import annotations

import hashlib
import json
import math
import pickle
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


SEED = 20260723
THRESHOLD = 0.35
NUMERIC_COLUMNS = ("signal_a", "signal_b", "noise", "redundant_signal")
CATEGORICAL_COLUMNS = ("channel",)
FEATURE_COLUMNS = (*NUMERIC_COLUMNS, *CATEGORICAL_COLUMNS)
FORMAT_VERSION = 1


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


def train_delivery_model(frame: pd.DataFrame) -> CalibratedClassifierCV:
    expected = (*FEATURE_COLUMNS, "target")
    if tuple(frame.columns) != expected or set(frame["target"].unique()) != {0, 1}:
        raise ValueError("training data does not match the v0.8 contract")
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    model = CalibratedClassifierCV(estimator=build_pipeline(), method="sigmoid", cv=folds)
    model.fit(frame.loc[:, FEATURE_COLUMNS], frame["target"])
    return model


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_artifact(directory: Path, model: CalibratedClassifierCV, training_rows: int) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    model_path = directory / "model.pkl"
    manifest_path = directory / "manifest.json"
    bundle = {
        "format_version": FORMAT_VERSION,
        "model": model,
        "threshold": THRESHOLD,
        "feature_columns": FEATURE_COLUMNS,
    }
    with model_path.open("wb") as handle:
        pickle.dump(bundle, handle, protocol=pickle.HIGHEST_PROTOCOL)
    manifest = {
        "format_version": FORMAT_VERSION,
        "model_file": model_path.name,
        "sha256": _sha256(model_path),
        "training_rows": training_rows,
        "feature_schema": {
            "numeric_nullable": list(NUMERIC_COLUMNS),
            "categorical_nullable": list(CATEGORICAL_COLUMNS),
            "additional_properties": False,
        },
        "threshold": THRESHOLD,
        "dependencies": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "trust_boundary": "load-local-reviewed-artifacts-only",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def load_artifact(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format_version") != FORMAT_VERSION:
        raise ValueError("unsupported-format-version")
    model_path = manifest_path.parent / manifest.get("model_file", "")
    if not model_path.is_file() or _sha256(model_path) != manifest.get("sha256"):
        raise ValueError("checksum-mismatch")
    expected_dependencies = {
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
    }
    if manifest.get("dependencies") != expected_dependencies:
        raise ValueError("dependency-version-mismatch")
    with model_path.open("rb") as handle:
        bundle = pickle.load(handle)
    if (
        bundle.get("format_version") != FORMAT_VERSION
        or tuple(bundle.get("feature_columns", ())) != FEATURE_COLUMNS
        or bundle.get("threshold") != manifest.get("threshold")
    ):
        raise ValueError("bundle-contract-mismatch")
    return bundle


def validate_record(record: dict[str, Any]) -> None:
    if set(record) != set(FEATURE_COLUMNS):
        raise ValueError("missing-or-additional-feature")
    for column in NUMERIC_COLUMNS:
        value = record[column]
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise ValueError(f"invalid-numeric-feature:{column}")
    channel = record["channel"]
    if channel is not None and (not isinstance(channel, str) or not channel.strip()):
        raise ValueError("invalid-categorical-feature:channel")


def predict_record(bundle: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    validate_record(record)
    model = bundle["model"]
    frame = pd.DataFrame([{column: record[column] for column in FEATURE_COLUMNS}])
    probability = float(model.predict_proba(frame)[0, 1])
    threshold = float(bundle["threshold"])
    return {
        "positive_probability": probability,
        "threshold": threshold,
        "decision": probability >= threshold,
    }


def fixed_report() -> str:
    frame = build_dataset()
    model = train_delivery_model(frame)
    sample = {
        "signal_a": 1.2,
        "signal_b": 0.4,
        "noise": -0.1,
        "redundant_signal": 0.6,
        "channel": "direct",
    }
    direct_probability = float(model.predict_proba(pd.DataFrame([sample]))[0, 1])
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        manifest_path = save_artifact(directory, model, len(frame))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        bundle = load_artifact(manifest_path)
        prediction = predict_record(bundle, sample)
        roundtrip_match = prediction["positive_probability"] == direct_probability
        try:
            predict_record(bundle, {key: value for key, value in sample.items() if key != "noise"})
        except ValueError as error:
            invalid_status = str(error)
        else:
            invalid_status = "accepted"
        (directory / "model.pkl").write_bytes((directory / "model.pkl").read_bytes() + b"tampered")
        try:
            load_artifact(manifest_path)
        except ValueError as error:
            tamper_status = str(error)
        else:
            tamper_status = "accepted"
    return "\n".join([
        f"artifact_format={FORMAT_VERSION},training_rows={len(frame)},features={len(FEATURE_COLUMNS)}",
        f"manifest=model.pkl,sha256_length={len(manifest['sha256'])},threshold={manifest['threshold']:.2f}",
        f"dependencies=numpy:{np.__version__},pandas:{pd.__version__},scikit-learn:{sklearn.__version__}",
        f"roundtrip_probability_match={str(roundtrip_match).lower()}",
        f"valid_inference=probability:{prediction['positive_probability']:.3f},decision:{str(prediction['decision']).lower()}",
        f"invalid_schema=rejected:{invalid_status}",
        f"tampered_artifact=rejected:{tamper_status}",
        "unsafe_load=trusted-reviewed-artifacts-only",
        "invariants=full-pipeline-persisted,schema-validated,manifest-verified",
    ])


if __name__ == "__main__":
    print(fixed_report())
