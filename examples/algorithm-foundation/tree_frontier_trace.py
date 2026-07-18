from __future__ import annotations

from collections import deque


CHILDREN: dict[int, tuple[int | None, int | None]] = {
    7: (3, 9),
    3: (None, 5),
    9: (8, 11),
    5: (None, None),
    8: (None, None),
    11: (None, None),
}


def show(values: list[int] | deque[int]) -> str:
    return "[" + ",".join(str(value) for value in values) + "]"


def trace_dfs() -> None:
    stack = [7]
    maximum = 1
    while stack:
        node = stack.pop()
        left, right = CHILDREN[node]
        if right is not None:
            stack.append(right)
        if left is not None:
            stack.append(left)
        maximum = max(maximum, len(stack))
        print(f"dfs pop={node} frontier={show(stack)}")
    print(f"dfs max_frontier={maximum}")


def trace_bfs() -> None:
    queue = deque([7])
    maximum = 1
    while queue:
        node = queue.popleft()
        left, right = CHILDREN[node]
        if left is not None:
            queue.append(left)
        if right is not None:
            queue.append(right)
        maximum = max(maximum, len(queue))
        print(f"bfs pop={node} frontier={show(queue)}")
    print(f"bfs max_frontier={maximum}")


def main() -> None:
    trace_dfs()
    trace_bfs()


if __name__ == "__main__":
    main()
