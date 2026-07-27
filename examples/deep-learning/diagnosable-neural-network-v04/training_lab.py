from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn


SEED = 20260723
FEATURE_COUNT = 2
HIDDEN_WIDTH = 4
CLASS_COUNT = 2
TRAIN_PER_CLASS = 36
VALIDATION_PER_CLASS = 12
DEFAULT_BATCH_SIZE = 12
DEFAULT_EPOCHS = 30
DEFAULT_LEARNING_RATE = 0.1


@dataclass(frozen=True)
class TensorSplit:
    inputs: torch.Tensor
    targets: torch.Tensor


@dataclass(frozen=True)
class DatasetSplits:
    train: TensorSplit
    validation: TensorSplit


@dataclass(frozen=True)
class EpochRecord:
    epoch: int
    mean_loss: float
    accuracy: float
    rows_seen: int


@dataclass(frozen=True)
class TrainingResult:
    history: tuple[EpochRecord, ...]
    steps: int
    parameter_update_norm: float


class TinyClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(FEATURE_COUNT, HIDDEN_WIDTH),
            nn.ReLU(),
            nn.Linear(HIDDEN_WIDTH, CLASS_COUNT),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


def _class_rows(center: float, rows: int, generator: torch.Generator) -> torch.Tensor:
    return torch.randn((rows, FEATURE_COUNT), generator=generator) * 0.55 + center


def build_splits(seed: int = SEED) -> DatasetSplits:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    train_inputs = torch.cat((
        _class_rows(-1.0, TRAIN_PER_CLASS, generator),
        _class_rows(1.0, TRAIN_PER_CLASS, generator),
    )).to(torch.float32)
    train_targets = torch.cat((
        torch.zeros(TRAIN_PER_CLASS, dtype=torch.int64),
        torch.ones(TRAIN_PER_CLASS, dtype=torch.int64),
    ))
    validation_inputs = torch.cat((
        _class_rows(-1.0, VALIDATION_PER_CLASS, generator),
        _class_rows(1.0, VALIDATION_PER_CLASS, generator),
    )).to(torch.float32)
    validation_targets = torch.cat((
        torch.zeros(VALIDATION_PER_CLASS, dtype=torch.int64),
        torch.ones(VALIDATION_PER_CLASS, dtype=torch.int64),
    ))
    train_order = torch.randperm(train_inputs.shape[0], generator=generator)
    validation_order = torch.randperm(validation_inputs.shape[0], generator=generator)
    return DatasetSplits(
        TensorSplit(train_inputs[train_order], train_targets[train_order]),
        TensorSplit(validation_inputs[validation_order], validation_targets[validation_order]),
    )


def build_model(seed: int = SEED) -> TinyClassifier:
    torch.manual_seed(seed)
    return TinyClassifier()


def evaluate(model: nn.Module, split: TensorSplit) -> tuple[float, float]:
    model.eval()
    with torch.no_grad():
        logits = model(split.inputs)
        loss = nn.CrossEntropyLoss()(logits, split.targets)
        accuracy = (logits.argmax(dim=1) == split.targets).to(torch.float32).mean()
    return float(loss), float(accuracy)


def epoch_batches(rows: int, batch_size: int, seed: int, epoch: int) -> tuple[torch.Tensor, ...]:
    if batch_size < 1 or batch_size > rows:
        raise ValueError("batch_size must be within training rows")
    generator = torch.Generator(device="cpu").manual_seed(seed + epoch)
    order = torch.randperm(rows, generator=generator)
    return tuple(order[start:start + batch_size] for start in range(0, rows, batch_size))


def train(
    model: nn.Module,
    train_split: TensorSplit,
    *,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    epochs: int = DEFAULT_EPOCHS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    seed: int = SEED,
) -> TrainingResult:
    if not math.isfinite(learning_rate) or learning_rate < 0:
        raise ValueError("learning_rate must be finite and non-negative")
    if epochs < 1:
        raise ValueError("epochs must be positive")
    batches_per_epoch = epoch_batches(train_split.inputs.shape[0], batch_size, seed, 0)
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()
    before = tuple(parameter.detach().clone() for parameter in model.parameters())
    history: list[EpochRecord] = []
    steps = 0
    for epoch in range(epochs):
        model.train()
        loss_sum = 0.0
        correct = 0
        rows_seen = 0
        for indexes in epoch_batches(train_split.inputs.shape[0], batch_size, seed, epoch):
            inputs, targets = train_split.inputs[indexes], train_split.targets[indexes]
            optimizer.zero_grad(set_to_none=True)
            logits = model(inputs)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()
            loss_sum += float(loss.detach()) * inputs.shape[0]
            correct += int((logits.detach().argmax(dim=1) == targets).sum())
            rows_seen += inputs.shape[0]
            steps += 1
        history.append(EpochRecord(epoch + 1, loss_sum / rows_seen, correct / rows_seen, rows_seen))
    update_squared = sum(
        float((after.detach() - initial).pow(2).sum())
        for after, initial in zip(model.parameters(), before)
    )
    expected_steps = len(batches_per_epoch) * epochs
    if steps != expected_steps:
        raise RuntimeError("training step count does not match batch contract")
    return TrainingResult(tuple(history), steps, math.sqrt(update_squared))


def fixed_report() -> str:
    splits = build_splits()
    model = build_model()
    initial_loss, initial_accuracy = evaluate(model, splits.train)
    validation_snapshot = splits.validation.inputs.clone()
    result = train(model, splits.train)
    final_loss, final_accuracy = evaluate(model, splits.train)
    zero_model = build_model()
    zero_result = train(zero_model, splits.train, learning_rate=0.0, epochs=1)
    return "\n".join([
        f"torch_version={torch.__version__}",
        f"split=train:{splits.train.inputs.shape[0]},validation:{splits.validation.inputs.shape[0]},classes=train:0:{TRAIN_PER_CLASS},1:{TRAIN_PER_CLASS};validation:0:{VALIDATION_PER_CLASS},1:{VALIDATION_PER_CLASS}",
        f"optimizer=SGD,learning_rate={DEFAULT_LEARNING_RATE},batch_size={DEFAULT_BATCH_SIZE},epochs={DEFAULT_EPOCHS}",
        f"initial_train=loss:{initial_loss:.6f},accuracy:{initial_accuracy:.3f}",
        f"final_train=loss:{final_loss:.6f},accuracy:{final_accuracy:.3f}",
        f"history=epochs:{len(result.history)},steps:{result.steps},rows_per_epoch:{result.history[-1].rows_seen}",
        f"parameter_update_norm={result.parameter_update_norm:.6f}",
        "batch_order=seeded-per-epoch",
        f"learning_rate_zero=no_parameter_change:{str(zero_result.parameter_update_norm == 0.0).lower()}",
        f"validation_untouched={str(torch.equal(validation_snapshot, splits.validation.inputs)).lower()}",
        "invalid_hyperparameter=rejected",
        "invariants=zero-backward-step,all-train-batches-once,history-recorded,validation-untouched",
    ])


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
