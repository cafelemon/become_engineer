from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import tempfile
from typing import Any

import torch
from torch import nn


ARTIFACT_VERSION = 1
MODEL_FILENAME = "model-state.pt"
MANIFEST_FILENAME = "manifest.json"
FEATURE_NAMES = ("signal_a", "signal_b")
LABELS = ("negative", "positive")
FEATURE_COUNT = 2
HIDDEN_WIDTH = 4
CLASS_COUNT = 2
DROPOUT = 0.25
THRESHOLD = 0.5


@dataclass(frozen=True)
class Prediction:
    label: str
    probabilities: tuple[float, float]


class DeliveryClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.hidden = nn.Linear(FEATURE_COUNT, HIDDEN_WIDTH)
        self.activation = nn.ReLU()
        self.dropout = nn.Dropout(DROPOUT)
        self.output = nn.Linear(HIDDEN_WIDTH, CLASS_COUNT)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        hidden = self.activation(self.hidden(inputs))
        return self.output(self.dropout(hidden))


def build_selected_model() -> DeliveryClassifier:
    model = DeliveryClassifier()
    with torch.no_grad():
        model.hidden.weight.copy_(torch.tensor([
            [1.0, 0.0],
            [-1.0, 0.0],
            [0.0, 1.0],
            [0.0, -1.0],
        ]))
        model.hidden.bias.fill_(0.1)
        model.output.weight.copy_(torch.tensor([
            [0.0, 1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        ]))
        model.output.bias.zero_()
    return model


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_torch_save(payload: Any, path: Path) -> None:
    with tempfile.NamedTemporaryFile(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
    try:
        torch.save(payload, temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json_save(payload: dict[str, Any], path: Path) -> None:
    with tempfile.NamedTemporaryFile(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        mode="w",
        encoding="utf-8",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def export_artifact(directory: Path, model: DeliveryClassifier) -> Path:
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    weights_path = directory / MODEL_FILENAME
    _atomic_torch_save(model.state_dict(), weights_path)
    manifest = {
        "artifact_version": ARTIFACT_VERSION,
        "artifact_id": "diagnosable-neural-network-v08",
        "architecture": "delivery-classifier-2x4x2",
        "model_file": MODEL_FILENAME,
        "model_sha256": _sha256(weights_path),
        "framework": {"name": "pytorch", "version": torch.__version__},
        "input_schema": {
            "fields": [
                {"name": FEATURE_NAMES[0], "dtype": "float32"},
                {"name": FEATURE_NAMES[1], "dtype": "float32"},
            ],
            "extra_fields": False,
            "finite_only": True,
        },
        "output_schema": {
            "labels": list(LABELS),
            "probability_count": CLASS_COUNT,
            "positive_threshold": THRESHOLD,
        },
    }
    manifest_path = directory / MANIFEST_FILENAME
    _atomic_json_save(manifest, manifest_path)
    return manifest_path


def _validate_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a mapping")
    if manifest.get("artifact_version") != ARTIFACT_VERSION:
        raise ValueError("unsupported artifact version")
    if manifest.get("artifact_id") != "diagnosable-neural-network-v08":
        raise ValueError("artifact identity mismatch")
    if manifest.get("architecture") != "delivery-classifier-2x4x2":
        raise ValueError("artifact architecture mismatch")
    if manifest.get("model_file") != MODEL_FILENAME:
        raise ValueError("artifact model path is not allowed")
    digest = manifest.get("model_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("artifact digest is invalid")
    framework = manifest.get("framework")
    if framework != {"name": "pytorch", "version": torch.__version__}:
        raise ValueError("framework version mismatch")
    expected_input = {
        "fields": [
            {"name": FEATURE_NAMES[0], "dtype": "float32"},
            {"name": FEATURE_NAMES[1], "dtype": "float32"},
        ],
        "extra_fields": False,
        "finite_only": True,
    }
    expected_output = {
        "labels": list(LABELS),
        "probability_count": CLASS_COUNT,
        "positive_threshold": THRESHOLD,
    }
    if manifest.get("input_schema") != expected_input:
        raise ValueError("input schema mismatch")
    if manifest.get("output_schema") != expected_output:
        raise ValueError("output schema mismatch")
    return manifest


def load_artifact(manifest_path: Path) -> tuple[DeliveryClassifier, dict[str, Any]]:
    manifest_path = manifest_path.resolve()
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = _validate_manifest(json.load(handle))
    weights_path = manifest_path.parent / MODEL_FILENAME
    if _sha256(weights_path) != manifest["model_sha256"]:
        raise ValueError("model digest mismatch")
    state_dict = torch.load(weights_path, map_location="cpu", weights_only=True)
    if not isinstance(state_dict, dict):
        raise ValueError("model state must be a mapping")
    model = DeliveryClassifier()
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    return model, manifest


def validate_record(record: Any) -> torch.Tensor:
    if not isinstance(record, dict):
        raise TypeError("input record must be a mapping")
    if set(record) != set(FEATURE_NAMES):
        raise ValueError(f"input fields must be exactly {FEATURE_NAMES}")
    values: list[float] = []
    for field in FEATURE_NAMES:
        value = record[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{field} must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError(f"{field} must be finite")
        values.append(numeric)
    return torch.tensor([values], dtype=torch.float32)


def predict(model: DeliveryClassifier, record: Any) -> Prediction:
    inputs = validate_record(record)
    model.eval()
    with torch.inference_mode():
        probabilities = torch.softmax(model(inputs), dim=1)[0]
    values = (float(probabilities[0]), float(probabilities[1]))
    label = LABELS[1] if values[1] >= THRESHOLD else LABELS[0]
    return Prediction(label, values)


def fixed_report() -> str:
    with tempfile.TemporaryDirectory() as directory:
        manifest_path = export_artifact(Path(directory), build_selected_model())
        model, manifest = load_artifact(manifest_path)
        negative = predict(model, {"signal_a": -1.0, "signal_b": 0.0})
        positive = predict(model, {"signal_a": 1.0, "signal_b": 0.0})
    return "\n".join([
        f"torch_version={torch.__version__}",
        "artifact=diagnosable-neural-network-v08,version:1,files:model-state.pt|manifest.json",
        "architecture=2->4->2,activation:relu,dropout:0.25",
        "input_schema=signal_a:float32,signal_b:float32,extra:false,finite:true",
        "output_schema=labels:negative|positive,probabilities:2,threshold:0.5",
        f"negative_case=label:{negative.label},probabilities:{negative.probabilities[0]:.6f}|{negative.probabilities[1]:.6f}",
        f"positive_case=label:{positive.label},probabilities:{positive.probabilities[0]:.6f}|{positive.probabilities[1]:.6f}",
        "inference=eval:true,inference_mode:true,requires_grad:false,deterministic:true",
        f"integrity=sha256:{len(manifest['model_sha256'])}-hex,verified-before-load",
        "load=map_location:cpu,weights_only:true,strict:true",
        "invalid_input=missing|extra|type|nonfinite:rejected",
        "tampered_model=rejected",
        "invariants=state-dict-only,manifest-validated,trusted-local-artifact,no-network,no-personal-data",
    ])


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
