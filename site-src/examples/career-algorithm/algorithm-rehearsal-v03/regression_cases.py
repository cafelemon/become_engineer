"""五类错因的修复后回归目标。"""

from __future__ import annotations

from collections import deque


def parse_counted_values(raw_input: str) -> list[int]:
    tokens = raw_input.split()
    if not tokens:
        raise ValueError("missing count")
    count = int(tokens[0])
    values = [int(token) for token in tokens[1:]]
    if count < 0 or len(values) != count:
        raise ValueError("count mismatch")
    return values


def stable_unique(values: list[int]) -> list[int]:
    return sorted(set(values))


def shortest_hops(graph: dict[str, list[str]], start: str, goal: str) -> int | None:
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        node, distance = queue.popleft()
        if node == goal:
            return distance
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
    return None


def linear_membership(values: list[int], queries: list[int]) -> tuple[list[bool], int]:
    lookup = set(values)
    checks = 0
    answers = []
    for query in queries:
        checks += 1
        answers.append(query in lookup)
    return answers, checks


def should_switch(has_invariant: bool, passing_boundary_case: bool, checkpoint_reached: bool) -> bool:
    return checkpoint_reached and not (has_invariant or passing_boundary_case)
