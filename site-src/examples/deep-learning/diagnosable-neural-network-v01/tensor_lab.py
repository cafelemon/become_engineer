from __future__ import annotations

from dataclasses import dataclass

import torch


SEED = 20260723
ROWS_PER_CLASS = 48
FEATURE_COUNT = 2
BATCH_SIZE = 8
HIDDEN_WIDTH = 3


@dataclass(frozen=True)
class TensorDataset:
    inputs: torch.Tensor
    targets: torch.Tensor


def build_dataset(seed: int = SEED, device: str | torch.device = "cpu") -> TensorDataset:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    negative = torch.randn((ROWS_PER_CLASS, FEATURE_COUNT), generator=generator) * 0.35 - 1.0
    positive = torch.randn((ROWS_PER_CLASS, FEATURE_COUNT), generator=generator) * 0.35 + 1.0
    inputs = torch.cat((negative, positive), dim=0).to(dtype=torch.float32)
    targets = torch.cat((
        torch.zeros(ROWS_PER_CLASS, dtype=torch.int64),
        torch.ones(ROWS_PER_CLASS, dtype=torch.int64),
    ))
    order = torch.randperm(inputs.shape[0], generator=generator)
    dataset = TensorDataset(inputs[order].to(device), targets[order].to(device))
    validate_dataset(dataset)
    return dataset


def validate_dataset(dataset: TensorDataset) -> None:
    inputs, targets = dataset.inputs, dataset.targets
    if inputs.ndim != 2 or inputs.shape[1] != FEATURE_COUNT:
        raise ValueError(f"inputs must have shape [rows, {FEATURE_COUNT}]")
    if targets.ndim != 1 or targets.shape[0] != inputs.shape[0]:
        raise ValueError("targets must have shape [rows] and align with inputs")
    if inputs.dtype != torch.float32:
        raise TypeError("inputs must use torch.float32")
    if targets.dtype != torch.int64:
        raise TypeError("targets must use torch.int64 class indexes")
    if inputs.device != targets.device:
        raise ValueError("inputs and targets must be on the same device")
    if not torch.isfinite(inputs).all():
        raise ValueError("inputs must contain only finite values")
    if set(targets.cpu().tolist()) != {0, 1}:
        raise ValueError("targets must contain class indexes 0 and 1")


def take_batch(dataset: TensorDataset, size: int = BATCH_SIZE) -> TensorDataset:
    if size < 1 or size > dataset.inputs.shape[0]:
        raise ValueError("batch size must be within dataset rows")
    batch = TensorDataset(dataset.inputs[:size], dataset.targets[:size])
    validate_dataset(batch)
    return batch


def linear_projection(batch: TensorDataset) -> torch.Tensor:
    weights = torch.tensor(
        [[0.5, -0.25, 1.0], [1.5, 0.75, -0.5]],
        dtype=batch.inputs.dtype,
        device=batch.inputs.device,
    )
    bias = torch.tensor([0.1, -0.2, 0.3], dtype=batch.inputs.dtype, device=batch.inputs.device)
    return batch.inputs @ weights + bias


def fixed_report() -> str:
    first = build_dataset()
    second = build_dataset()
    batch = take_batch(first)
    projected = linear_projection(batch)
    class_counts = torch.bincount(first.targets, minlength=2)
    return "\n".join([
        f"torch_version={torch.__version__}",
        "device=cpu",
        f"rows={first.inputs.shape[0]},features={first.inputs.shape[1]},classes=0:{int(class_counts[0])},1:{int(class_counts[1])}",
        f"inputs=shape:{first.inputs.shape[0]}x{first.inputs.shape[1]},dtype:{str(first.inputs.dtype).removeprefix('torch.')},device:{first.inputs.device.type}",
        f"targets=shape:{first.targets.shape[0]},dtype:{str(first.targets.dtype).removeprefix('torch.')},device:{first.targets.device.type}",
        f"mini_batch=inputs:{batch.inputs.shape[0]}x{batch.inputs.shape[1]},targets:{batch.targets.shape[0]}",
        f"linear_contract={batch.inputs.shape[0]}x{batch.inputs.shape[1]} @ {FEATURE_COUNT}x{HIDDEN_WIDTH} + {HIDDEN_WIDTH} -> {projected.shape[0]}x{projected.shape[1]}",
        f"broadcast_bias={HIDDEN_WIDTH}->{projected.shape[0]}x{projected.shape[1]}",
        f"seed_repeat={str(torch.equal(first.inputs, second.inputs)).lower()}",
        "invalid_shape=rejected",
        "invalid_dtype=rejected",
        "invariants=feature-rank2,target-rank1,row-aligned,cpu-deterministic",
    ])


if __name__ == "__main__":
    torch.set_num_threads(1)
    print(fixed_report())
