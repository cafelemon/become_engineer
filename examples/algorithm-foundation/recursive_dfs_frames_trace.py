from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    value: int
    left: Node | None = None
    right: Node | None = None


def trace_preorder(root: Node | None) -> None:
    stack: list[int] = []

    def visit(node: Node | None, depth: int) -> None:
        if node is None:
            return
        stack.append(node.value)
        print(f"enter value={node.value} depth={depth} stack={stack}")
        print(f"record value={node.value} order=preorder")
        visit(node.left, depth + 1)
        visit(node.right, depth + 1)
        stack.pop()
        print(f"leave value={node.value} resume={stack[-1] if stack else 'done'}")

    visit(root, 0)


def main() -> None:
    tree = Node(7, Node(3, right=Node(5)), Node(9))
    trace_preorder(tree)


if __name__ == "__main__":
    main()
