from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(slots=True)
class _Node:
    value: int
    slot_index: int
    left: _Node | None = None
    right: _Node | None = None


@dataclass(frozen=True, slots=True)
class ShapeTrace:
    size: int
    height: int
    leaf_count: int


@dataclass(frozen=True, slots=True)
class SlotPath:
    value: int
    directions: tuple[str, ...]


class BinaryTree:
    """A validated tree that keeps canonical slots and private linked nodes."""

    def __init__(self, values: Sequence[int | None]) -> None:
        copied = list(values)
        if copied and copied[0] is None:
            raise ValueError("non-empty tree requires a root value")
        while copied and copied[-1] is None:
            copied.pop()
        for index, value in enumerate(copied):
            if index > 0 and value is not None and copied[(index - 1) // 2] is None:
                raise ValueError(f"slot {index} has no parent")

        self._slots = tuple(copied)
        self._root = self._build_node(0)

    @property
    def slots(self) -> tuple[int | None, ...]:
        return self._slots

    @property
    def _root_node(self) -> _Node | None:
        return self._root

    def slot_value(self, index: int) -> int:
        if index < 0:
            raise IndexError("slot index must be non-negative")
        if index >= len(self._slots):
            raise IndexError("slot index out of range")
        value = self._slots[index]
        if value is None:
            raise IndexError("slot is empty")
        return value

    def _build_node(self, index: int) -> _Node | None:
        if index >= len(self._slots) or self._slots[index] is None:
            return None
        value = self._slots[index]
        assert value is not None
        node = _Node(value, index)
        node.left = self._build_node(index * 2 + 1)
        node.right = self._build_node(index * 2 + 2)
        return node


def describe_shape(tree: BinaryTree) -> ShapeTrace:
    def visit(node: _Node | None, depth: int) -> tuple[int, int, int]:
        if node is None:
            return 0, depth - 1, 0
        left_size, left_height, left_leaves = visit(node.left, depth + 1)
        right_size, right_height, right_leaves = visit(node.right, depth + 1)
        leaves = 1 if node.left is None and node.right is None else left_leaves + right_leaves
        return 1 + left_size + right_size, max(depth, left_height, right_height), leaves

    size, height, leaves = visit(tree._root_node, 0)
    return ShapeTrace(size, height, leaves)


def path_to_slot(tree: BinaryTree, index: int) -> SlotPath:
    value = tree.slot_value(index)
    directions: list[str] = []
    cursor = index
    while cursor > 0:
        directions.append("L" if cursor % 2 == 1 else "R")
        cursor = (cursor - 1) // 2
    directions.reverse()
    return SlotPath(value, tuple(directions))
