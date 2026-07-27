from __future__ import annotations

import os
from dataclasses import dataclass

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEED = 20260723
NUMERIC_COLUMNS = ("signal_a", "signal_b", "noise", "redundant_signal")


@dataclass(frozen=True)
class UnsupervisedResult:
    transformed: np.ndarray
    labels: np.ndarray
    explained_variance_ratio: tuple[float, float]
    inertia: float
    silhouette: float
    cluster_sizes: tuple[int, ...]


def build_dataset(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    latent_group = np.concatenate((np.zeros(80, dtype=np.int64), np.ones(40, dtype=np.int64)))
    signal_a = latent_group * 1.5 + rng.normal(0, 1, latent_group.size)
    signal_b = latent_group * 0.8 + rng.normal(0, 1, latent_group.size)
    noise = rng.normal(0, 1, latent_group.size)
    redundant_signal = signal_a * 0.5 + rng.normal(0, 0.2, latent_group.size)
    order = rng.permutation(latent_group.size)
    frame = pd.DataFrame({
        "sample_id": pd.Series([f"sample-{index:03d}" for index in range(latent_group.size)], dtype="string").iloc[order].reset_index(drop=True),
        "signal_a": signal_a[order],
        "signal_b": signal_b[order],
        "noise": noise[order],
        "redundant_signal": redundant_signal[order],
        "target": latent_group[order],
    })
    frame.loc[frame.index % 11 == 0, "signal_a"] = np.nan
    frame.loc[frame.index % 17 == 0, "signal_b"] = np.nan
    return frame


def feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    expected = ("sample_id", *NUMERIC_COLUMNS, "target")
    if tuple(frame.columns) != expected or not frame["sample_id"].is_unique:
        raise ValueError("dataset does not match the v0.6 contract")
    if not all(pd.api.types.is_numeric_dtype(frame[column]) for column in NUMERIC_COLUMNS):
        raise ValueError("unsupervised numeric features must remain numeric")
    return frame.loc[:, NUMERIC_COLUMNS].copy(deep=True)


def build_projection() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=2, svd_solver="full")),
    ])


def run_unsupervised(frame: pd.DataFrame, clusters: int = 2, seed: int = SEED) -> UnsupervisedResult:
    if clusters < 2 or clusters >= len(frame):
        raise ValueError("clusters must be between 2 and rows - 1")
    values = feature_matrix(frame)
    projection = build_projection()
    transformed = projection.fit_transform(values)
    model = KMeans(n_clusters=clusters, n_init=20, random_state=seed, algorithm="lloyd")
    labels = model.fit_predict(transformed)
    pca = projection.named_steps["pca"]
    sizes = tuple(int(count) for count in np.bincount(labels, minlength=clusters))
    return UnsupervisedResult(
        transformed=transformed,
        labels=labels,
        explained_variance_ratio=tuple(float(value) for value in pca.explained_variance_ratio_),
        inertia=float(model.inertia_),
        silhouette=float(silhouette_score(transformed, labels)),
        cluster_sizes=sizes,
    )


def fixed_report() -> str:
    frame = build_dataset()
    raw_features = feature_matrix(frame)
    result = run_unsupervised(frame, 2, SEED)
    alternative_seed = run_unsupervised(frame, 2, SEED + 1)
    candidate_scores = {k: run_unsupervised(frame, k, SEED).silhouette for k in (2, 3, 4)}
    stability = adjusted_rand_score(result.labels, alternative_seed.labels)
    return "\n".join([
        f"rows={len(frame)},features={len(NUMERIC_COLUMNS)},target_used_for_fit=false",
        "preprocess=median-impute,standard-scale,pca:2",
        f"explained_variance=pc1:{result.explained_variance_ratio[0]:.3f},pc2:{result.explained_variance_ratio[1]:.3f},total:{sum(result.explained_variance_ratio):.3f}",
        f"kmeans=k:2,n_init:20,inertia:{result.inertia:.3f},silhouette:{result.silhouette:.3f}",
        f"cluster_sizes={','.join(str(size) for size in result.cluster_sizes)}",
        "candidate_silhouette=" + ",".join(f"k{k}:{score:.3f}" for k, score in candidate_scores.items()),
        f"seed_stability_adjusted_rand={stability:.3f}",
        f"raw_features_unchanged={str(raw_features.equals(feature_matrix(frame))).lower()}",
        "interpretation=clusters-are-descriptive-not-ground-truth",
        "invariants=no-target-fit,scaled-before-pca,fixed-random-state",
    ])


if __name__ == "__main__":
    print(fixed_report())
