from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


SEED = 20260723
ROWS_PER_CLASS = 48
FEATURE_COUNT = 2
BATCH_SIZE = 8
HIDDEN_WIDTH = 4
CLASS_COUNT = 2


@dataclass(frozen=True)
class TensorDataset:
    inputs: torch.Tensor
    targets: torch.Tensor


@dataclass(frozen=True)
class ForwardTrace:
    hidden_linear: torch.Tensor
    hidden_active: torch.Tensor
    logits: torch.Tensor


def build_dataset(seed: int = SEED) -> TensorDataset:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    negative = torch.randn((ROWS_PER_CLASS, FEATURE_COUNT), generator=generator) * 0.35 - 1.0
    positive = torch.randn((ROWS_PER_CLASS, FEATURE_COUNT), generator=generator) * 0.35 + 1.0
    inputs = torch.cat((negative, positive), dim=0).to(dtype=torch.float32)
    targets = torch.cat((
        torch.zeros(ROWS_PER_CLASS, dtype=torch.int64),
        torch.ones(ROWS_PER_CLASS, dtype=torch.int64),
    ))
    order = torch.randperm(inputs.shape[0], generator=generator)
    return TensorDataset(inputs[order], targets[order])


def take_batch(dataset: TensorDataset, size: int = BATCH_SIZE) -> TensorDataset:
    if dataset.inputs.ndim != 2 or dataset.inputs.shape[1] != FEATURE_COUNT:
        raise ValueError(f"inputs must have shape [rows, {FEATURE_COUNT}]")
    if dataset.targets.ndim != 1 or dataset.targets.shape[0] != dataset.inputs.shape[0]:
        raise ValueError("targets must align with input rows")
    if size < 1 or size > dataset.inputs.shape[0]:
        raise ValueError("batch size must be within dataset rows")
    return TensorDataset(dataset.inputs[:size], dataset.targets[:size])


class TinyClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fc1 = nn.Linear(FEATURE_COUNT, HIDDEN_WIDTH)
        self.activation = nn.ReLU()
        self.fc2 = nn.Linear(HIDDEN_WIDTH, CLASS_COUNT)

    def trace(self, inputs: torch.Tensor) -> ForwardTrace:
        if inputs.ndim != 2 or inputs.shape[1] != FEATURE_COUNT:
            raise ValueError(f"inputs must have shape [batch, {FEATURE_COUNT}]")
        if inputs.dtype != torch.float32:
            raise TypeError("inputs must use torch.float32")
        hidden_linear = self.fc1(inputs)
        hidden_active = self.activation(hidden_linear)
        logits = self.fc2(hidden_active)
        return ForwardTrace(hidden_linear, hidden_active, logits)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.trace(inputs).logits


def build_model(seed: int = SEED) -> TinyClassifier:
    torch.manual_seed(seed)
    return TinyClassifier()


def count_trainable_parameters(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


def fixed_report() -> str:
    batch = take_batch(build_dataset())
    first = build_model()
    second = build_model()
    trace = first.trace(batch.inputs)
    probabilities = torch.softmax(trace.logits, dim=1)
    parameter_shapes = {name: tuple(parameter.shape) for name, parameter in first.named_parameters()}
    return "\n".join([
        f"torch_version={torch.__version__}",
        f"batch={batch.inputs.shape[0]}x{batch.inputs.shape[1]}",
        "module=TinyClassifier",
        f"fc1=weight:{parameter_shapes['fc1.weight'][0]}x{parameter_shapes['fc1.weight'][1]},bias:{parameter_shapes['fc1.bias'][0]}",
        f"relu={trace.hidden_active.shape[0]}x{trace.hidden_active.shape[1]}",
        f"fc2=weight:{parameter_shapes['fc2.weight'][0]}x{parameter_shapes['fc2.weight'][1]},bias:{parameter_shapes['fc2.bias'][0]}",
        f"forward={batch.inputs.shape[0]}x{batch.inputs.shape[1]}->{trace.hidden_linear.shape[0]}x{trace.hidden_linear.shape[1]}->{trace.hidden_active.shape[0]}x{trace.hidden_active.shape[1]}->{trace.logits.shape[0]}x{trace.logits.shape[1]}",
        f"parameters=trainable:{count_trainable_parameters(first)},tensors:{len(list(first.parameters()))}",
        f"logits=shape:{trace.logits.shape[0]}x{trace.logits.shape[1]},requires_grad:{str(trace.logits.requires_grad).lower()}",
        f"probability_rows_sum_one={str(torch.allclose(probabilities.sum(dim=1), torch.ones(batch.inputs.shape[0]))).lower()}",
        f"deterministic_initialization={str(all(torch.equal(left, right) for left, right in zip(first.parameters(), second.parameters()))).lower()}",
        "invalid_feature_width=rejected",
        "invariants=module-registered,parameter-shapes-explicit,forward-batch-preserved,no-training-yet",
    ])


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
