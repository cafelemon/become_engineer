from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch import nn


SEED = 20260723
FEATURE_COUNT = 2
HIDDEN_WIDTH = 16
CLASS_COUNT = 2
BATCH_SIZE = 32
HEALTHY_SCALE = 0.35
EXPLOSIVE_LOSS_SCALE = 1000.0
CLIP_THRESHOLD = 1.0


@dataclass(frozen=True)
class TensorBatch:
    inputs: torch.Tensor
    targets: torch.Tensor


@dataclass(frozen=True)
class ForwardTrace:
    hidden_1: torch.Tensor
    hidden_2: torch.Tensor
    logits: torch.Tensor


@dataclass(frozen=True)
class DiagnosticSnapshot:
    loss: float
    activation_nonzero_1: float
    activation_nonzero_2: float
    activation_max: float
    gradient_norms: tuple[tuple[str, float], ...]
    global_gradient_norm: float


class DiagnosticClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fc1 = nn.Linear(FEATURE_COUNT, HIDDEN_WIDTH)
        self.fc2 = nn.Linear(HIDDEN_WIDTH, HIDDEN_WIDTH)
        self.output = nn.Linear(HIDDEN_WIDTH, CLASS_COUNT)
        self.activation = nn.ReLU()

    def trace(self, inputs: torch.Tensor) -> ForwardTrace:
        validate_inputs(inputs)
        hidden_1 = self.activation(self.fc1(inputs))
        hidden_2 = self.activation(self.fc2(hidden_1))
        logits = self.output(hidden_2)
        return ForwardTrace(hidden_1, hidden_2, logits)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.trace(inputs).logits


def build_batch(seed: int = SEED) -> TensorBatch:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    inputs = torch.randn((BATCH_SIZE, FEATURE_COUNT), generator=generator)
    targets = ((inputs[:, 0] + 0.5 * inputs[:, 1]) > 0).to(torch.int64)
    return TensorBatch(inputs.to(torch.float32), targets)


def validate_inputs(inputs: torch.Tensor) -> None:
    if inputs.ndim != 2 or inputs.shape[1] != FEATURE_COUNT:
        raise ValueError(f"inputs must have shape [batch, {FEATURE_COUNT}]")
    if inputs.dtype != torch.float32:
        raise TypeError("inputs must use torch.float32")
    if not bool(torch.isfinite(inputs).all()):
        raise ValueError("inputs must contain only finite values")


def build_model(scale: float = HEALTHY_SCALE, seed: int = SEED) -> DiagnosticClassifier:
    if not math.isfinite(scale) or scale < 0:
        raise ValueError("initialization scale must be finite and non-negative")
    torch.manual_seed(seed)
    model = DiagnosticClassifier()
    generator = torch.Generator(device="cpu").manual_seed(seed)
    with torch.no_grad():
        for module in model.modules():
            if isinstance(module, nn.Linear):
                module.weight.normal_(mean=0.0, std=scale, generator=generator)
                module.bias.zero_()
    return model


def _global_gradient_norm(model: nn.Module) -> float:
    total = sum(
        float(parameter.grad.detach().pow(2).sum())
        for parameter in model.parameters()
        if parameter.grad is not None
    )
    return math.sqrt(total)


def diagnose(
    model: DiagnosticClassifier,
    batch: TensorBatch,
    *,
    loss_scale: float = 1.0,
) -> DiagnosticSnapshot:
    if not math.isfinite(loss_scale) or loss_scale <= 0:
        raise ValueError("loss_scale must be finite and positive")
    model.zero_grad(set_to_none=True)
    trace = model.trace(batch.inputs)
    loss = nn.CrossEntropyLoss()(trace.logits, batch.targets) * loss_scale
    if not bool(torch.isfinite(loss)):
        raise FloatingPointError("loss is not finite")
    loss.backward()
    gradient_norms: list[tuple[str, float]] = []
    for name, parameter in model.named_parameters():
        if parameter.grad is None or not bool(torch.isfinite(parameter.grad).all()):
            raise FloatingPointError(f"gradient is missing or non-finite: {name}")
        gradient_norms.append((name, float(parameter.grad.norm())))
    return DiagnosticSnapshot(
        float(loss.detach()),
        float((trace.hidden_1 > 0).to(torch.float32).mean()),
        float((trace.hidden_2 > 0).to(torch.float32).mean()),
        max(float(trace.hidden_1.detach().max()), float(trace.hidden_2.detach().max())),
        tuple(gradient_norms),
        _global_gradient_norm(model),
    )


def clip_explosive_gradients(
    model: DiagnosticClassifier,
    batch: TensorBatch,
    threshold: float = CLIP_THRESHOLD,
) -> tuple[float, float]:
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("clip threshold must be finite and positive")
    snapshot = diagnose(model, batch, loss_scale=EXPLOSIVE_LOSS_SCALE)
    before = snapshot.global_gradient_norm
    returned = float(nn.utils.clip_grad_norm_(model.parameters(), max_norm=threshold))
    after = _global_gradient_norm(model)
    if not math.isclose(before, returned, rel_tol=1e-5):
        raise RuntimeError("clip_grad_norm returned an unexpected pre-clip norm")
    return before, after


def zero_initialization_stalls_hidden_gradients(batch: TensorBatch) -> bool:
    model = build_model(scale=0.0)
    diagnose(model, batch)
    return (
        bool(torch.equal(model.fc1.weight.grad, torch.zeros_like(model.fc1.weight.grad)))
        and bool(torch.equal(model.fc2.weight.grad, torch.zeros_like(model.fc2.weight.grad)))
        and bool(torch.equal(model.output.weight.grad, torch.zeros_like(model.output.weight.grad)))
    )


def fixed_report() -> str:
    batch = build_batch()
    healthy_model = build_model()
    healthy = diagnose(healthy_model, batch)
    before, after = clip_explosive_gradients(build_model(), batch)
    gradient_text = ",".join(f"{name}:{value:.6f}" for name, value in healthy.gradient_norms)
    return "\n".join([
        f"torch_version={torch.__version__}",
        f"model={FEATURE_COUNT}->{HIDDEN_WIDTH}->{HIDDEN_WIDTH}->{CLASS_COUNT},batch={BATCH_SIZE}",
        f"initialization=normal,std:{HEALTHY_SCALE},bias:zero,seed:{SEED}",
        f"activation=relu,nonzero_rates:{healthy.activation_nonzero_1:.3f}|{healthy.activation_nonzero_2:.3f},max:{healthy.activation_max:.6f}",
        f"loss={healthy.loss:.6f},finite:true",
        f"gradient_norms={gradient_text}",
        f"global_gradient_norm={healthy.global_gradient_norm:.6f}",
        f"explosive_loss_scale={EXPLOSIVE_LOSS_SCALE:.0f},clip_threshold={CLIP_THRESHOLD:.1f},before:{before:.6f},after:{after:.6f}",
        f"zero_initialization=hidden_gradients_stalled:{str(zero_initialization_stalls_hidden_gradients(batch)).lower()}",
        "nonfinite_input=rejected",
        "invalid_clip_threshold=rejected",
        "invariants=activations-observed,layer-gradients-finite,clip-after-backward-before-step,root-cause-still-required",
    ])


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
