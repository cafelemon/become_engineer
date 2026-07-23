from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Mapping, Sequence


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


@dataclass(frozen=True)
class ExperimentConfig:
    seed: int
    threshold: float
    schema_version: str
    split_policy: str


def dataset_fingerprint(rows: Sequence[Mapping[str, object]]) -> str:
    if not rows or any("sample_id" not in row for row in rows):
        raise ValueError("dataset needs rows with sample_id")
    if len({str(row["sample_id"]) for row in rows}) != len(rows):
        raise ValueError("sample_id must be unique")
    ordered = sorted((dict(row) for row in rows), key=lambda row: str(row["sample_id"]))
    return _digest(ordered)


def build_manifest(
    config: ExperimentConfig,
    rows: Sequence[Mapping[str, object]],
    metrics: Mapping[str, float],
    artifacts: Mapping[str, bytes],
    *,
    code_revision: str,
) -> dict[str, object]:
    if not code_revision or any(not name or name.startswith("/") or ".." in name.split("/") for name in artifacts):
        raise ValueError("revision and artifact names must be safe and explicit")
    return {
        "manifest_version": 1,
        "code_revision": code_revision,
        "config": asdict(config),
        "config_sha256": _digest(asdict(config)),
        "data_sha256": dataset_fingerprint(rows),
        "metrics": dict(sorted(metrics.items())),
        "artifacts": {name: sha256(content).hexdigest() for name, content in sorted(artifacts.items())},
    }


def verify_manifest(
    manifest: Mapping[str, object],
    config: ExperimentConfig,
    rows: Sequence[Mapping[str, object]],
    artifacts: Mapping[str, bytes],
) -> tuple[bool, tuple[str, ...]]:
    failures: list[str] = []
    if manifest.get("config_sha256") != _digest(asdict(config)):
        failures.append("config")
    if manifest.get("data_sha256") != dataset_fingerprint(rows):
        failures.append("data")
    expected_artifacts = {name: sha256(content).hexdigest() for name, content in sorted(artifacts.items())}
    if manifest.get("artifacts") != expected_artifacts:
        failures.append("artifacts")
    return not failures, tuple(failures)


def fixed_report() -> str:
    config = ExperimentConfig(20260723, 0.5, "samples-v1", "stratified-1-per-label")
    rows = (
        {"sample_id": "b", "label": 0, "score": 0.3},
        {"sample_id": "a", "label": 1, "score": 0.9},
    )
    artifacts = {"metrics.json": b'{"accuracy":1.0}\n', "predictions.csv": b"sample_id,prediction\na,1\nb,0\n"}
    manifest = build_manifest(config, rows, {"accuracy": 1.0}, artifacts, code_revision="teaching-v06")
    verified, failures = verify_manifest(manifest, config, tuple(reversed(rows)), artifacts)
    tampered, tampered_failures = verify_manifest(
        manifest, config, rows, {**artifacts, "metrics.json": b'{"accuracy":0.0}\n'}
    )
    return "\n".join([
        f"manifest_version={manifest['manifest_version']}",
        f"code_revision={manifest['code_revision']}",
        f"config_sha256={str(manifest['config_sha256'])[:12]}",
        f"data_sha256={str(manifest['data_sha256'])[:12]}",
        f"artifact_count={len(artifacts)}",
        f"verify={'pass' if verified else ','.join(failures)}",
        f"tampered={'pass' if tampered else ','.join(tampered_failures)}",
        "invariants=canonical-config,stable-data-order,artifact-integrity",
    ])


if __name__ == "__main__":
    print(fixed_report())
