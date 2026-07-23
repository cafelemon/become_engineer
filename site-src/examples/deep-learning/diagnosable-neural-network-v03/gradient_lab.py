from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn


SEED = 20260723
ROWS_PER_CLASS = 48
FEATURE_COUNT = 2
BATCH_SIZE = 8
HIDDEN_WIDTH = 4
CLASS_COUNT = 2
EPSILON = 1e-3


@dataclass(frozen=True)
class TensorBatch:
    inputs: torch.Tensor
    targets: torch.Tensor


@dataclass(frozen=True)
class GradientCheck:
    parameter: str
    autograd: float
    numerical: float
    absolute_error: float


def build_batch(seed: int = SEED, size: int = BATCH_SIZE) -> TensorBatch:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    negative = torch.randn((ROWS_PER_CLASS, FEATURE_COUNT), generator=generator) * 0.35 - 1.0
    positive = torch.randn((ROWS_PER_CLASS, FEATURE_COUNT), generator=generator) * 0.35 + 1.0
    inputs = torch.cat((negative, positive), dim=0).to(torch.float32)
    targets = torch.cat((
        torch.zeros(ROWS_PER_CLASS, dtype=torch.int64),
        torch.ones(ROWS_PER_CLASS, dtype=torch.int64),
    ))
    order = torch.randperm(inputs.shape[0], generator=generator)
    if size < 1 or size > inputs.shape[0]:
        raise ValueError("batch size must be within dataset rows")
    return TensorBatch(inputs[order][:size], targets[order][:size])


class TinyClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fc1 = nn.Linear(FEATURE_COUNT, HIDDEN_WIDTH)
        self.activation = nn.ReLU()
        self.fc2 = nn.Linear(HIDDEN_WIDTH, CLASS_COUNT)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        if inputs.ndim != 2 or inputs.shape[1] != FEATURE_COUNT:
            raise ValueError(f"inputs must have shape [batch, {FEATURE_COUNT}]")
        return self.fc2(self.activation(self.fc1(inputs)))


def build_model(seed: int = SEED) -> TinyClassifier:
    torch.manual_seed(seed)
    return TinyClassifier()


def validate_targets(targets: torch.Tensor, rows: int) -> None:
    if targets.ndim != 1 or targets.shape[0] != rows:
        raise ValueError("targets must have shape [batch]")
    if targets.dtype != torch.int64:
        raise TypeError("CrossEntropyLoss targets must use torch.int64")
    if not bool(((targets >= 0) & (targets < CLASS_COUNT)).all()):
        raise ValueError("target class index is outside logits columns")


def loss_for(model: nn.Module, batch: TensorBatch) -> torch.Tensor:
    validate_targets(batch.targets, batch.inputs.shape[0])
    logits = model(batch.inputs)
    return nn.CrossEntropyLoss()(logits, batch.targets)


def backward_once(model: nn.Module, batch: TensorBatch) -> torch.Tensor:
    model.zero_grad(set_to_none=True)
    loss = loss_for(model, batch)
    loss.backward()
    return loss


def global_gradient_norm(model: nn.Module) -> float:
    squared = sum(
        float(parameter.grad.detach().pow(2).sum())
        for parameter in model.parameters()
        if parameter.grad is not None
    )
    return math.sqrt(squared)


def finite_difference_check(
    model: TinyClassifier,
    batch: TensorBatch,
    epsilon: float = EPSILON,
) -> GradientCheck:
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    backward_once(model, batch)
    parameter = model.fc2.weight
    autograd = float(parameter.grad[0, 1])
    original = float(parameter[0, 1].detach())
    with torch.no_grad():
        parameter[0, 1] = original + epsilon
    plus = float(loss_for(model, batch).detach())
    with torch.no_grad():
        parameter[0, 1] = original - epsilon
    minus = float(loss_for(model, batch).detach())
    with torch.no_grad():
        parameter[0, 1] = original
    numerical = (plus - minus) / (2 * epsilon)
    return GradientCheck(
        parameter="fc2.weight[0,1]",
        autograd=autograd,
        numerical=numerical,
        absolute_error=abs(autograd - numerical),
    )


def accumulation_ratio(model: nn.Module, batch: TensorBatch) -> float:
    model.zero_grad(set_to_none=True)
    loss_for(model, batch).backward()
    first = model.fc2.bias.grad.detach().clone()
    loss_for(model, batch).backward()
    second = model.fc2.bias.grad.detach().clone()
    nonzero = first.abs() > 1e-12
    return float((second[nonzero] / first[nonzero]).mean())


def fixed_report() -> str:
    batch = build_batch()
    model = build_model()
    loss = backward_once(model, batch)
    gradients = [parameter.grad for parameter in model.parameters()]
    check = finite_difference_check(build_model(), batch)
    ratio = accumulation_ratio(build_model(), batch)
    zeroed = build_model()
    backward_once(zeroed, batch)
    zeroed.zero_grad(set_to_none=True)
    return "\n".join([
        f"torch_version={torch.__version__}",
        f"batch={batch.inputs.shape[0]}x{batch.inputs.shape[1]},targets={batch.targets.shape[0]}",
        f"loss=cross_entropy:{float(loss.detach()):.6f},requires_grad:{str(loss.requires_grad).lower()}",
        f"backward=parameter_gradients:{sum(gradient is not None for gradient in gradients)},finite:{str(all(bool(torch.isfinite(gradient).all()) for gradient in gradients if gradient is not None)).lower()}",
        f"gradient_norm={global_gradient_norm(model):.6f}",
        f"finite_difference=parameter:{check.parameter},autograd:{check.autograd:.6f},numerical:{check.numerical:.6f},abs_error:{check.absolute_error:.6f}",
        f"accumulation=second_backward:{ratio:.3f}x",
        f"zero_grad=set_to_none:{str(all(parameter.grad is None for parameter in zeroed.parameters())).lower()}",
        "invalid_target=rejected",
        "invariants=loss-from-logits,backward-once-per-graph,gradients-checked,zero-before-next-step",
    ])


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
