from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from traceable_tree_traversal_lab.tree import BinaryTree, _Node


class TraversalDepthError(RuntimeError):
    """Raised before a traversal enters a node beyond its teaching limit."""


@dataclass(frozen=True, slots=True)
class RecursiveTrace:
    values: tuple[int, ...]
    visits: int
    max_depth: int


@dataclass(frozen=True, slots=True)
class DepthCount:
    count: int
    visits: int


@dataclass(frozen=True, slots=True)
class TraversalTrace:
    values: tuple[int, ...]
    visits: int
    max_frontier: int


@dataclass(frozen=True, slots=True)
class LevelRow:
    depth: int
    values: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class WidthTrace:
    depth: int | None
    width: int
    visits: int


def _recursive_traversal(tree: BinaryTree, order: str, max_depth: int | None) -> RecursiveTrace:
    if max_depth is not None and max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    values: list[int] = []
    deepest = -1

    def visit(node: _Node | None, depth: int) -> None:
        nonlocal deepest
        if node is None:
            return
        if max_depth is not None and depth > max_depth:
            raise TraversalDepthError(f"node depth {depth} exceeds limit {max_depth}")
        deepest = max(deepest, depth)
        if order == "preorder":
            values.append(node.value)
        visit(node.left, depth + 1)
        if order == "inorder":
            values.append(node.value)
        visit(node.right, depth + 1)
        if order == "postorder":
            values.append(node.value)

    visit(tree._root_node, 0)
    return RecursiveTrace(tuple(values), len(values), deepest)


def recursive_preorder(tree: BinaryTree, max_depth: int | None = None) -> RecursiveTrace:
    return _recursive_traversal(tree, "preorder", max_depth)


def recursive_inorder(tree: BinaryTree, max_depth: int | None = None) -> RecursiveTrace:
    return _recursive_traversal(tree, "inorder", max_depth)


def recursive_postorder(tree: BinaryTree, max_depth: int | None = None) -> RecursiveTrace:
    return _recursive_traversal(tree, "postorder", max_depth)


def count_at_depth(tree: BinaryTree, depth: int) -> DepthCount:
    if depth < 0:
        raise ValueError("depth must be non-negative")
    count = 0
    visits = 0

    def visit(node: _Node | None, current: int) -> None:
        nonlocal count, visits
        if node is None:
            return
        visits += 1
        if current == depth:
            count += 1
            return
        visit(node.left, current + 1)
        visit(node.right, current + 1)

    visit(tree._root_node, 0)
    return DepthCount(count, visits)


def iterative_preorder(tree: BinaryTree) -> TraversalTrace:
    root = tree._root_node
    if root is None:
        return TraversalTrace((), 0, 0)
    frontier = [root]
    values: list[int] = []
    maximum = 1
    while frontier:
        node = frontier.pop()
        values.append(node.value)
        if node.right is not None:
            frontier.append(node.right)
            maximum = max(maximum, len(frontier))
        if node.left is not None:
            frontier.append(node.left)
            maximum = max(maximum, len(frontier))
    return TraversalTrace(tuple(values), len(values), maximum)


def breadth_first(tree: BinaryTree) -> TraversalTrace:
    root = tree._root_node
    if root is None:
        return TraversalTrace((), 0, 0)
    frontier = deque([root])
    values: list[int] = []
    maximum = 1
    while frontier:
        node = frontier.popleft()
        values.append(node.value)
        if node.left is not None:
            frontier.append(node.left)
            maximum = max(maximum, len(frontier))
        if node.right is not None:
            frontier.append(node.right)
            maximum = max(maximum, len(frontier))
    return TraversalTrace(tuple(values), len(values), maximum)


def build_level_rows(tree: BinaryTree) -> tuple[LevelRow, ...]:
    root = tree._root_node
    if root is None:
        return ()
    frontier = deque([(root, 0)])
    rows: list[list[int]] = []
    while frontier:
        node, depth = frontier.popleft()
        if depth == len(rows):
            rows.append([])
        rows[depth].append(node.value)
        if node.left is not None:
            frontier.append((node.left, depth + 1))
        if node.right is not None:
            frontier.append((node.right, depth + 1))
    return tuple(LevelRow(depth, tuple(values)) for depth, values in enumerate(rows))


def widest_level(tree: BinaryTree) -> WidthTrace:
    rows = build_level_rows(tree)
    visits = sum(len(row.values) for row in rows)
    if not rows:
        return WidthTrace(None, 0, 0)
    widest = max(rows, key=lambda row: len(row.values))
    return WidthTrace(widest.depth, len(widest.values), visits)
