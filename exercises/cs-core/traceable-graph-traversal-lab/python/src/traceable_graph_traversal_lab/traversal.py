from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .graph import Edge, UndirectedGraph


@dataclass(frozen=True, slots=True)
class BfsTrace:
    order: tuple[int, ...]
    distances: tuple[int | None, ...]
    parents: tuple[int | None, ...]
    visits: int
    edge_checks: int
    max_frontier: int


@dataclass(frozen=True, slots=True)
class PathTrace:
    path: tuple[int, ...]
    distance: int | None


@dataclass(frozen=True, slots=True)
class DfsTrace:
    components: tuple[tuple[int, ...], ...]
    visits: int
    edge_checks: int
    max_depth: int
    cycle_edge: Edge | None


@dataclass(frozen=True, slots=True)
class ComponentLabels:
    labels: tuple[int, ...]
    component_count: int


def breadth_first(graph: UndirectedGraph, start: int) -> BfsTrace:
    graph.neighbors(start)
    distances: list[int | None] = [None] * graph.vertex_count
    parents: list[int | None] = [None] * graph.vertex_count
    distances[start] = 0
    frontier: deque[int] = deque([start])
    order: list[int] = []
    edge_checks = 0
    max_frontier = 1

    while frontier:
        vertex = frontier.popleft()
        order.append(vertex)
        for neighbor in graph.neighbors(vertex):
            edge_checks += 1
            if distances[neighbor] is None:
                distance = distances[vertex]
                assert distance is not None
                distances[neighbor] = distance + 1
                parents[neighbor] = vertex
                frontier.append(neighbor)
                max_frontier = max(max_frontier, len(frontier))

    return BfsTrace(
        tuple(order), tuple(distances), tuple(parents), len(order), edge_checks, max_frontier
    )


def shortest_path(graph: UndirectedGraph, start: int, target: int) -> PathTrace:
    graph.neighbors(target)
    trace = breadth_first(graph, start)
    distance = trace.distances[target]
    if distance is None:
        return PathTrace((), None)
    path: list[int] = []
    cursor: int | None = target
    while cursor is not None:
        path.append(cursor)
        cursor = trace.parents[cursor]
    path.reverse()
    return PathTrace(tuple(path), distance)


def reachable_within(graph: UndirectedGraph, start: int, max_distance: int) -> tuple[int, ...]:
    if max_distance < 0:
        raise ValueError("max_distance must be non-negative")
    trace = breadth_first(graph, start)
    result: list[int] = []
    for vertex in trace.order:
        distance = trace.distances[vertex]
        if distance is not None and distance <= max_distance:
            result.append(vertex)
    return tuple(result)


def depth_first_components(graph: UndirectedGraph) -> DfsTrace:
    visited = [False] * graph.vertex_count
    components: list[tuple[int, ...]] = []
    visits = 0
    edge_checks = 0
    max_depth = -1
    cycle_edge: Edge | None = None

    def visit(vertex: int, parent: int | None, depth: int, component: list[int]) -> None:
        nonlocal visits, edge_checks, max_depth, cycle_edge
        visited[vertex] = True
        visits += 1
        max_depth = max(max_depth, depth)
        component.append(vertex)
        for neighbor in graph.neighbors(vertex):
            edge_checks += 1
            if not visited[neighbor]:
                visit(neighbor, vertex, depth + 1, component)
            elif neighbor != parent and cycle_edge is None:
                cycle_edge = Edge(min(vertex, neighbor), max(vertex, neighbor))

    for start in range(graph.vertex_count):
        if not visited[start]:
            component: list[int] = []
            visit(start, None, 0, component)
            components.append(tuple(component))

    return DfsTrace(tuple(components), visits, edge_checks, max_depth, cycle_edge)


def build_component_labels(graph: UndirectedGraph) -> ComponentLabels:
    trace = depth_first_components(graph)
    labels = [-1] * graph.vertex_count
    for label, component in enumerate(trace.components):
        for vertex in component:
            labels[vertex] = label
    return ComponentLabels(tuple(labels), len(trace.components))
