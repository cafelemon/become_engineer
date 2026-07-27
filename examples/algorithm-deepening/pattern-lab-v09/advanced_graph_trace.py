from __future__ import annotations

from collections import deque
from heapq import heappop, heappush
from typing import Sequence

Edge = tuple[str, str]


def _graph(nodes: Sequence[str], edges: Sequence[Edge]) -> dict[str, list[str]]:
    if len(set(nodes)) != len(nodes) or any(left not in nodes or right not in nodes for left, right in edges):
        raise ValueError("invalid graph")
    adjacency = {node: [] for node in nodes}
    for left, right in edges:
        adjacency[left].append(right)
    for neighbors in adjacency.values():
        neighbors.sort()
    return adjacency


def topological_order(nodes: Sequence[str], edges: Sequence[Edge]) -> tuple[str, ...] | None:
    adjacency = _graph(nodes, edges)
    indegree = {node: 0 for node in nodes}
    for _, right in edges:
        indegree[right] += 1
    ready: list[str] = []
    for node in nodes:
        if indegree[node] == 0:
            heappush(ready, node)
    order: list[str] = []
    while ready:
        node = heappop(ready)
        order.append(node)
        for neighbor in adjacency[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heappush(ready, neighbor)
    return tuple(order) if len(order) == len(nodes) else None


def strongly_connected_components(nodes: Sequence[str], edges: Sequence[Edge]) -> tuple[tuple[str, ...], ...]:
    adjacency = _graph(nodes, edges)
    reverse = _graph(nodes, [(right, left) for left, right in edges])
    seen: set[str] = set()
    finish: list[str] = []

    def visit(node: str) -> None:
        seen.add(node)
        for neighbor in adjacency[node]:
            if neighbor not in seen:
                visit(neighbor)
        finish.append(node)

    for node in sorted(nodes):
        if node not in seen:
            visit(node)

    seen.clear()
    components: list[tuple[str, ...]] = []

    def collect(node: str, current: list[str]) -> None:
        seen.add(node)
        current.append(node)
        for neighbor in reverse[node]:
            if neighbor not in seen:
                collect(neighbor, current)

    for node in reversed(finish):
        if node not in seen:
            current: list[str] = []
            collect(node, current)
            components.append(tuple(sorted(current)))
    return tuple(sorted(components, key=lambda component: component[0]))


def condensation_edges(components: Sequence[Sequence[str]], edges: Sequence[Edge]) -> tuple[tuple[int, int], ...]:
    owner = {node: index for index, component in enumerate(components) for node in component}
    return tuple(sorted({(owner[left], owner[right]) for left, right in edges if owner[left] != owner[right]}))


def multi_source_distances(nodes: Sequence[str], edges: Sequence[Edge], sources: Sequence[str]) -> dict[str, int | None]:
    adjacency = _graph(nodes, edges)
    if not sources or any(source not in adjacency for source in sources):
        raise ValueError("invalid sources")
    distance: dict[str, int | None] = {node: None for node in nodes}
    queue = deque()
    for source in sorted(set(sources)):
        distance[source] = 0
        queue.append(source)
    while queue:
        node = queue.popleft()
        for neighbor in adjacency[node]:
            if distance[neighbor] is None:
                distance[neighbor] = distance[node] + 1  # type: ignore[operator]
                queue.append(neighbor)
    return distance


def fixed_report() -> str:
    nodes = list("ABCDEF")
    dag = [("A","C"),("B","C"),("C","D"),("C","E"),("D","F"),("E","F")]
    cyclic = [("A","B"),("B","C"),("C","A"),("C","D"),("D","E"),("E","D"),("E","F")]
    components = strongly_connected_components(nodes, cyclic)
    distances = multi_source_distances(nodes, dag, ["A", "B"])
    return "\n".join([
        "dag_edges=A>C,B>C,C>D,C>E,D>F,E>F",
        f"topological={','.join(topological_order(nodes, dag) or ())}",
        f"cycle_topological={'cycle' if topological_order(nodes, cyclic) is None else 'unexpected'}",
        "scc_edges=A>B,B>C,C>A,C>D,D>E,E>D,E>F",
        f"scc={'|'.join(','.join(component) for component in components)}",
        f"condensation={','.join(f'{left}>{right}' for left,right in condensation_edges(components, cyclic))}",
        f"sources=A,B distances={','.join(f'{node}:{distances[node]}' for node in nodes)}",
        "invariants=zero-indegree-only,scc-condensation-acyclic,first-discovery-shortest",
    ])


if __name__ == "__main__":
    print(fixed_report())

