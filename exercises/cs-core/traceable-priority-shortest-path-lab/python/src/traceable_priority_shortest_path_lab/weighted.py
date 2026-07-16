from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Iterable

MAX_DISTANCE = (1 << 63) - 1


@dataclass(frozen=True, order=True, slots=True)
class WeightedEdge:
    u: int
    v: int
    weight: int


@dataclass(frozen=True, slots=True)
class RelaxationEvent:
    from_vertex: int
    to_vertex: int
    old_distance: int | None
    candidate: int
    updated: bool


@dataclass(frozen=True, slots=True)
class DijkstraTrace:
    settled: tuple[int, ...]
    distances: tuple[int | None, ...]
    parents: tuple[int | None, ...]
    edge_checks: int
    relaxations: int
    queue_pushes: int
    stale_pops: int
    max_frontier: int
    events: tuple[RelaxationEvent, ...]


@dataclass(frozen=True, slots=True)
class WeightedPath:
    path: tuple[int, ...]
    distance: int | None


class WeightedGraph:
    def __init__(self, vertex_count: int, edges: Iterable[tuple[int, int, int] | WeightedEdge]) -> None:
        if vertex_count < 0:
            raise ValueError("vertex_count must be non-negative")
        canonical: list[WeightedEdge] = []
        seen: set[tuple[int, int]] = set()
        for raw_edge in edges:
            u, v, weight = (
                (raw_edge.u, raw_edge.v, raw_edge.weight)
                if isinstance(raw_edge, WeightedEdge)
                else raw_edge
            )
            if u < 0 or v < 0 or u >= vertex_count or v >= vertex_count:
                raise ValueError("edge endpoint out of range")
            if u == v:
                raise ValueError("self-loops are not allowed")
            if weight < 0:
                raise ValueError("edge weight must be non-negative")
            if weight > MAX_DISTANCE:
                raise OverflowError("edge weight exceeds signed 64-bit range")
            pair = (min(u, v), max(u, v))
            if pair in seen:
                raise ValueError("duplicate edges are not allowed")
            seen.add(pair)
            canonical.append(WeightedEdge(pair[0], pair[1], weight))
        canonical.sort()
        adjacency: list[list[tuple[int, int]]] = [[] for _ in range(vertex_count)]
        for edge in canonical:
            adjacency[edge.u].append((edge.v, edge.weight))
            adjacency[edge.v].append((edge.u, edge.weight))
        for neighbors in adjacency:
            neighbors.sort()
        self._vertex_count = vertex_count
        self._edges = tuple(canonical)
        self._adjacency = tuple(tuple(neighbors) for neighbors in adjacency)

    @property
    def vertex_count(self) -> int:
        return self._vertex_count

    @property
    def edges(self) -> tuple[WeightedEdge, ...]:
        return self._edges

    def neighbors(self, vertex: int) -> tuple[tuple[int, int], ...]:
        self.check_vertex(vertex)
        return self._adjacency[vertex]

    def check_vertex(self, vertex: int) -> None:
        if vertex < 0 or vertex >= self._vertex_count:
            raise IndexError("vertex out of range")


def dijkstra(graph: WeightedGraph, start: int) -> DijkstraTrace:
    graph.check_vertex(start)
    distances: list[int | None] = [None] * graph.vertex_count
    parents: list[int | None] = [None] * graph.vertex_count
    distances[start] = 0
    queue: list[tuple[int, int, int]] = [(0, 0, start)]
    sequence = 1
    settled: list[int] = []
    events: list[RelaxationEvent] = []
    edge_checks = 0
    relaxations = 0
    queue_pushes = 1
    stale_pops = 0
    max_frontier = 1
    while queue:
        distance, _, vertex = heapq.heappop(queue)
        if distances[vertex] != distance:
            stale_pops += 1
            continue
        settled.append(vertex)
        for neighbor, weight in graph.neighbors(vertex):
            edge_checks += 1
            if distance > MAX_DISTANCE - weight:
                raise OverflowError("shortest-path distance exceeds signed 64-bit range")
            candidate = distance + weight
            old_distance = distances[neighbor]
            updated = old_distance is None or candidate < old_distance
            events.append(RelaxationEvent(vertex, neighbor, old_distance, candidate, updated))
            if updated:
                distances[neighbor] = candidate
                parents[neighbor] = vertex
                relaxations += 1
                heapq.heappush(queue, (candidate, sequence, neighbor))
                sequence += 1
                queue_pushes += 1
                max_frontier = max(max_frontier, len(queue))
    return DijkstraTrace(
        tuple(settled), tuple(distances), tuple(parents), edge_checks, relaxations,
        queue_pushes, stale_pops, max_frontier, tuple(events)
    )


def shortest_path(graph: WeightedGraph, start: int, target: int) -> WeightedPath:
    graph.check_vertex(target)
    trace = dijkstra(graph, start)
    distance = trace.distances[target]
    if distance is None:
        return WeightedPath((), None)
    path: list[int] = []
    current: int | None = target
    while current is not None:
        path.append(current)
        current = trace.parents[current]
    path.reverse()
    return WeightedPath(tuple(path), distance)


def vertices_within_distance(graph: WeightedGraph, start: int, max_distance: int) -> tuple[int, ...]:
    if max_distance < 0:
        raise ValueError("max_distance must be non-negative")
    if max_distance > MAX_DISTANCE:
        raise OverflowError("max_distance exceeds signed 64-bit range")
    trace = dijkstra(graph, start)
    result: list[int] = []
    for vertex in trace.settled:
        distance = trace.distances[vertex]
        if distance is not None and distance <= max_distance:
            result.append(vertex)
    return tuple(result)


def sample_weighted_graph() -> WeightedGraph:
    return WeightedGraph(7, (
        (0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1),
        (2, 3, 5), (3, 4, 3), (1, 4, 7), (4, 5, 1),
    ))
