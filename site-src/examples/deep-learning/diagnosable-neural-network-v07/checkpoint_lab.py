from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import tempfile
from typing import Any

import torch
from torch import nn


SEED = 20260723
FEATURE_COUNT = 2
HIDDEN_WIDTH = 12
CLASS_COUNT = 2
SAMPLE_COUNT = 64
BATCH_SIZE = 8
TOTAL_EPOCHS = 8
INTERRUPT_EPOCH = 3
LEARNING_RATE = 0.08
MOMENTUM = 0.9
DROPOUT = 0.2
CHECKPOINT_VERSION = 1


@dataclass(frozen=True)
class TrainingState:
    epoch: int
    history: tuple[float, ...]


@dataclass(frozen=True)
class ResumeEvidence:
    final_epoch: int
    continuous_history: tuple[float, ...]
    resumed_history: tuple[float, ...]
    model_equal: bool
    optimizer_equal: bool
    rng_equal_at_load: bool
    digest: str


class RecoverableClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(FEATURE_COUNT, HIDDEN_WIDTH),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(HIDDEN_WIDTH, CLASS_COUNT),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


def build_dataset() -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator(device="cpu").manual_seed(SEED + 1)
    inputs = torch.randn((SAMPLE_COUNT, FEATURE_COUNT), generator=generator)
    targets = ((inputs[:, 0] - 0.35 * inputs[:, 1]) > 0).to(torch.int64)
    return inputs.to(torch.float32), targets


def build_training_objects() -> tuple[RecoverableClassifier, torch.optim.SGD]:
    torch.manual_seed(SEED)
    model = RecoverableClassifier()
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=LEARNING_RATE,
        momentum=MOMENTUM,
    )
    return model, optimizer


def _validate_state(state: TrainingState) -> None:
    if state.epoch < 0 or state.epoch > TOTAL_EPOCHS:
        raise ValueError("epoch is outside the configured training range")
    if len(state.history) != state.epoch:
        raise ValueError("history length must equal the completed epoch count")
    if not all(math.isfinite(value) and value >= 0 for value in state.history):
        raise ValueError("history contains an invalid loss")


def train_until(
    model: RecoverableClassifier,
    optimizer: torch.optim.SGD,
    state: TrainingState,
    end_epoch: int,
) -> TrainingState:
    _validate_state(state)
    if end_epoch < state.epoch or end_epoch > TOTAL_EPOCHS:
        raise ValueError("end_epoch must continue the current run")
    inputs, targets = build_dataset()
    history = list(state.history)
    model.train()
    for _epoch in range(state.epoch, end_epoch):
        order = torch.randperm(SAMPLE_COUNT)
        total_loss = 0.0
        for start in range(0, SAMPLE_COUNT, BATCH_SIZE):
            batch_indices = order[start : start + BATCH_SIZE]
            optimizer.zero_grad(set_to_none=True)
            logits = model(inputs[batch_indices])
            loss = nn.CrossEntropyLoss()(logits, targets[batch_indices])
            loss.backward()
            optimizer.step()
            total_loss += float(loss.detach()) * len(batch_indices)
        history.append(total_loss / SAMPLE_COUNT)
    return TrainingState(end_epoch, tuple(history))


def _checkpoint_payload(
    model: RecoverableClassifier,
    optimizer: torch.optim.SGD,
    state: TrainingState,
) -> dict[str, Any]:
    _validate_state(state)
    return {
        "checkpoint_version": CHECKPOINT_VERSION,
        "architecture": "recoverable-classifier-2x12x2",
        "config": {
            "seed": SEED,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "momentum": MOMENTUM,
            "dropout": DROPOUT,
            "total_epochs": TOTAL_EPOCHS,
        },
        "epoch": state.epoch,
        "history": list(state.history),
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "torch_rng_state": torch.get_rng_state(),
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_checkpoint(
    path: Path,
    model: RecoverableClassifier,
    optimizer: torch.optim.SGD,
    state: TrainingState,
) -> str:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _checkpoint_payload(model, optimizer, state)
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
    return file_sha256(path)


def load_checkpoint(
    path: Path,
    expected_digest: str,
) -> tuple[RecoverableClassifier, torch.optim.SGD, TrainingState]:
    path = path.resolve()
    if len(expected_digest) != 64 or file_sha256(path) != expected_digest:
        raise ValueError("checkpoint digest mismatch")
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if not isinstance(payload, dict):
        raise ValueError("checkpoint payload must be a mapping")
    if payload.get("checkpoint_version") != CHECKPOINT_VERSION:
        raise ValueError("unsupported checkpoint version")
    if payload.get("architecture") != "recoverable-classifier-2x12x2":
        raise ValueError("checkpoint architecture mismatch")
    config = payload.get("config")
    expected_config = {
        "seed": SEED,
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "momentum": MOMENTUM,
        "dropout": DROPOUT,
        "total_epochs": TOTAL_EPOCHS,
    }
    if config != expected_config:
        raise ValueError("checkpoint configuration mismatch")
    try:
        state = TrainingState(
            int(payload["epoch"]),
            tuple(float(value) for value in payload["history"]),
        )
        model_state = payload["model_state_dict"]
        optimizer_state = payload["optimizer_state_dict"]
        rng_state = payload["torch_rng_state"]
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("checkpoint schema is incomplete") from error
    _validate_state(state)
    if not isinstance(rng_state, torch.Tensor) or rng_state.dtype != torch.uint8:
        raise ValueError("checkpoint RNG state is invalid")
    model, optimizer = build_training_objects()
    model.load_state_dict(model_state, strict=True)
    optimizer.load_state_dict(optimizer_state)
    torch.set_rng_state(rng_state)
    return model, optimizer, state


def _tensor_tree_equal(left: Any, right: Any) -> bool:
    if isinstance(left, torch.Tensor) and isinstance(right, torch.Tensor):
        return bool(torch.equal(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _tensor_tree_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(
            _tensor_tree_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def compare_continuous_and_resumed(directory: Path) -> ResumeEvidence:
    torch.manual_seed(SEED + 2)
    continuous_model, continuous_optimizer = build_training_objects()
    torch.manual_seed(SEED + 2)
    continuous_state = train_until(
        continuous_model,
        continuous_optimizer,
        TrainingState(0, ()),
        TOTAL_EPOCHS,
    )

    interrupted_model, interrupted_optimizer = build_training_objects()
    torch.manual_seed(SEED + 2)
    interrupted_state = train_until(
        interrupted_model,
        interrupted_optimizer,
        TrainingState(0, ()),
        INTERRUPT_EPOCH,
    )
    checkpoint = directory / "training-v07.pt"
    digest = save_checkpoint(
        checkpoint,
        interrupted_model,
        interrupted_optimizer,
        interrupted_state,
    )
    saved_rng_state = torch.get_rng_state().clone()
    _ = torch.rand(19)
    resumed_model, resumed_optimizer, loaded_state = load_checkpoint(checkpoint, digest)
    rng_equal_at_load = bool(torch.equal(torch.get_rng_state(), saved_rng_state))
    resumed_state = train_until(
        resumed_model,
        resumed_optimizer,
        loaded_state,
        TOTAL_EPOCHS,
    )
    model_equal = _tensor_tree_equal(
        continuous_model.state_dict(),
        resumed_model.state_dict(),
    )
    optimizer_equal = _tensor_tree_equal(
        continuous_optimizer.state_dict(),
        resumed_optimizer.state_dict(),
    )
    return ResumeEvidence(
        resumed_state.epoch,
        continuous_state.history,
        resumed_state.history,
        model_equal,
        optimizer_equal,
        rng_equal_at_load,
        digest,
    )


def fixed_report() -> str:
    with tempfile.TemporaryDirectory() as directory:
        evidence = compare_continuous_and_resumed(Path(directory))
    history_equal = evidence.continuous_history == evidence.resumed_history
    return "\n".join([
        f"torch_version={torch.__version__}",
        f"model={FEATURE_COUNT}->{HIDDEN_WIDTH}->{CLASS_COUNT},dropout={DROPOUT},optimizer=SGD(momentum:{MOMENTUM})",
        f"schedule=total:{TOTAL_EPOCHS},interrupt:{INTERRUPT_EPOCH},batch:{BATCH_SIZE}",
        "checkpoint=model+optimizer+epoch+history+torch_rng_state",
        f"resume=epoch:{evidence.final_epoch},rng_restored:{str(evidence.rng_equal_at_load).lower()}",
        f"equivalence=history:{str(history_equal).lower()},model:{str(evidence.model_equal).lower()},optimizer:{str(evidence.optimizer_equal).lower()}",
        f"loss=first:{evidence.resumed_history[0]:.6f},final:{evidence.resumed_history[-1]:.6f}",
        f"integrity=sha256:{len(evidence.digest)}-hex,verified-before-load",
        "load=map_location:cpu,weights_only:true,schema:validated",
        "corrupt_checkpoint=rejected",
        "incompatible_checkpoint=rejected",
        "invariants=atomic-write,trusted-local-artifact,exact-resume,no-test-data",
    ])


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
