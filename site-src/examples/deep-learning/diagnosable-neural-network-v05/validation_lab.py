from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import math

import torch
from torch import nn


SEED = 20260723
FEATURE_COUNT = 2
CLASS_COUNT = 2
TRAIN_ROWS = 64
VALIDATION_ROWS = 256
NOISY_TRAIN_LABELS = 16
HIDDEN_WIDTH = 48
EPOCHS = 240
LEARNING_RATE = 0.05


@dataclass(frozen=True)
class TensorSplit:
    inputs: torch.Tensor
    targets: torch.Tensor


@dataclass(frozen=True)
class DatasetSplits:
    train: TensorSplit
    validation: TensorSplit
    clean_train_targets: torch.Tensor
    noisy_indexes: torch.Tensor


@dataclass(frozen=True)
class CandidateConfig:
    name: str
    weight_decay: float
    dropout: float


@dataclass(frozen=True)
class EpochRecord:
    epoch: int
    train_loss: float
    train_accuracy: float
    validation_loss: float
    validation_accuracy: float


@dataclass(frozen=True)
class CandidateResult:
    config: CandidateConfig
    best_epoch: int
    best_validation_loss: float
    best_validation_accuracy: float
    final_train_accuracy: float
    final_validation_loss: float
    final_validation_accuracy: float
    history: tuple[EpochRecord, ...]
    best_state: dict[str, torch.Tensor]


class RegularizedClassifier(nn.Module):
    def __init__(self, dropout: float) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(FEATURE_COUNT, HIDDEN_WIDTH),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(HIDDEN_WIDTH, HIDDEN_WIDTH),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(HIDDEN_WIDTH, CLASS_COUNT),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


def _make_split(rows: int, generator: torch.Generator) -> TensorSplit:
    inputs = torch.rand((rows, FEATURE_COUNT), generator=generator) * 3.0 - 1.5
    targets = ((inputs[:, 0] * inputs[:, 1]) > 0).to(torch.int64)
    return TensorSplit(inputs.to(torch.float32), targets)


def build_splits(seed: int = SEED) -> DatasetSplits:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    clean_train = _make_split(TRAIN_ROWS, generator)
    validation = _make_split(VALIDATION_ROWS, generator)
    noisy_indexes = torch.randperm(TRAIN_ROWS, generator=generator)[:NOISY_TRAIN_LABELS]
    noisy_targets = clean_train.targets.clone()
    noisy_targets[noisy_indexes] = 1 - noisy_targets[noisy_indexes]
    return DatasetSplits(
        TensorSplit(clean_train.inputs, noisy_targets),
        validation,
        clean_train.targets,
        noisy_indexes,
    )


def build_model(dropout: float, seed: int = SEED) -> RegularizedClassifier:
    if not 0.0 <= dropout < 1.0:
        raise ValueError("dropout must be within [0, 1)")
    torch.manual_seed(seed)
    return RegularizedClassifier(dropout)


def evaluate(model: nn.Module, split: TensorSplit) -> tuple[float, float]:
    model.eval()
    with torch.no_grad():
        logits = model(split.inputs)
        loss = nn.CrossEntropyLoss()(logits, split.targets)
        accuracy = (logits.argmax(dim=1) == split.targets).to(torch.float32).mean()
    return float(loss), float(accuracy)


def train_candidate(
    config: CandidateConfig,
    splits: DatasetSplits,
    *,
    epochs: int = EPOCHS,
    learning_rate: float = LEARNING_RATE,
    seed: int = SEED,
) -> CandidateResult:
    if epochs < 1:
        raise ValueError("epochs must be positive")
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("learning_rate must be finite and positive")
    if not math.isfinite(config.weight_decay) or config.weight_decay < 0:
        raise ValueError("weight_decay must be finite and non-negative")
    model = build_model(config.dropout, seed)
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=learning_rate,
        momentum=0.9,
        weight_decay=config.weight_decay,
    )
    criterion = nn.CrossEntropyLoss()
    history: list[EpochRecord] = []
    best_loss = math.inf
    best_accuracy = 0.0
    best_epoch = 0
    best_state: dict[str, torch.Tensor] = {}
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        logits = model(splits.train.inputs)
        loss = criterion(logits, splits.train.targets)
        loss.backward()
        optimizer.step()
        train_loss, train_accuracy = evaluate(model, splits.train)
        validation_loss, validation_accuracy = evaluate(model, splits.validation)
        history.append(EpochRecord(
            epoch,
            train_loss,
            train_accuracy,
            validation_loss,
            validation_accuracy,
        ))
        if validation_loss < best_loss:
            best_loss = validation_loss
            best_accuracy = validation_accuracy
            best_epoch = epoch
            best_state = deepcopy(model.state_dict())
    return CandidateResult(
        config,
        best_epoch,
        best_loss,
        best_accuracy,
        history[-1].train_accuracy,
        history[-1].validation_loss,
        history[-1].validation_accuracy,
        tuple(history),
        best_state,
    )


def select_candidate(results: tuple[CandidateResult, ...]) -> CandidateResult:
    if not results:
        raise ValueError("at least one candidate is required")
    return min(results, key=lambda item: (item.final_validation_loss, item.config.name))


def dropout_mode_probe(seed: int = SEED) -> tuple[bool, bool]:
    model = build_model(0.5, seed)
    inputs = build_splits(seed).validation.inputs[:8]
    model.train()
    torch.manual_seed(seed)
    train_first = model(inputs)
    train_second = model(inputs)
    model.eval()
    eval_first = model(inputs)
    eval_second = model(inputs)
    return not torch.equal(train_first, train_second), torch.equal(eval_first, eval_second)


def fixed_report() -> str:
    splits = build_splits()
    candidates = (
        CandidateConfig("unregularized", weight_decay=0.0, dropout=0.0),
        CandidateConfig("regularized", weight_decay=0.02, dropout=0.25),
    )
    results = tuple(train_candidate(config, splits) for config in candidates)
    selected = select_candidate(results)
    stochastic_train, stable_eval = dropout_mode_probe()
    lines = [
        f"torch_version={torch.__version__}",
        f"data=train:{TRAIN_ROWS},noisy_labels:{NOISY_TRAIN_LABELS},validation:{VALIDATION_ROWS},validation_labels:clean",
        f"budget=epochs:{EPOCHS},learning_rate:{LEARNING_RATE},optimizer:SGD-momentum",
    ]
    for result in results:
        lines.append(
            f"candidate={result.config.name},weight_decay:{result.config.weight_decay},dropout:{result.config.dropout},"
            f"best_epoch:{result.best_epoch},train_accuracy:{result.final_train_accuracy:.3f},"
            f"final_validation_loss:{result.final_validation_loss:.6f},final_validation_accuracy:{result.final_validation_accuracy:.3f},"
            f"best_validation_loss:{result.best_validation_loss:.6f}"
        )
    lines.extend([
        f"selected={selected.config.name},rule=lowest-final-validation-loss",
        f"dropout=train_stochastic:{str(stochastic_train).lower()},eval_stable:{str(stable_eval).lower()}",
        "validation_gradients=disabled",
        "test_set=not-used",
        "invalid_regularization=rejected",
        "invariants=same-data-initialization-budget,validation-only-selection,best-state-retained,test-untouched",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
