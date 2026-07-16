from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Iterable

from .dsu import DisjointSet

MIN_WEIGHT = -(1 << 63)
MAX_WEIGHT = (1 << 63) - 1


@dataclass(frozen=True, order=True, slots=True)
class SpanningEdge:
    u: int
    v: int
    weight: int


@dataclass(frozen=True, slots=True)
class KruskalEvent:
    edge: SpanningEdge
    accepted: bool
    components_before: int
    components_after: int


@dataclass(frozen=True, slots=True)
class SpanningForest:
    edges: tuple[SpanningEdge, ...]
    total_weight: int
    component_count: int
    events: tuple[KruskalEvent, ...]


@dataclass(frozen=True, slots=True)
class PrimEvent:
    edge: SpanningEdge
    accepted: bool


@dataclass(frozen=True, slots=True)
class PrimTrace:
    forest: SpanningForest
    component_starts: tuple[int, ...]
    edge_scans: int
    queue_pushes: int
    stale_pops: int
    max_frontier: int
    events: tuple[PrimEvent, ...]


@dataclass(frozen=True, slots=True)
class ForestComparison:
    matching: bool
    kruskal_weight: int
    prim_weight: int
    component_count: int
    expected_edge_count: int


class SpanningGraph:
    def __init__(self, vertex_count: int, edges: Iterable[tuple[int, int, int] | SpanningEdge]) -> None:
        if vertex_count < 0:
            raise ValueError("vertex_count must be non-negative")
        canonical: list[SpanningEdge] = []
        seen: set[tuple[int, int]] = set()
        for raw in edges:
            u, v, weight = (raw.u, raw.v, raw.weight) if isinstance(raw, SpanningEdge) else raw
            if u < 0 or v < 0 or u >= vertex_count or v >= vertex_count:
                raise ValueError("edge endpoint out of range")
            if u == v:
                raise ValueError("self-loops are not allowed")
            if weight < MIN_WEIGHT or weight > MAX_WEIGHT:
                raise OverflowError("edge weight exceeds signed 64-bit range")
            pair = (min(u, v), max(u, v))
            if pair in seen:
                raise ValueError("duplicate undirected edge")
            seen.add(pair)
            canonical.append(SpanningEdge(pair[0], pair[1], weight))
        canonical.sort(key=lambda edge: (edge.u, edge.v, edge.weight))
        adjacency: list[list[tuple[int, int, SpanningEdge]]] = [[] for _ in range(vertex_count)]
        for edge in canonical:
            adjacency[edge.u].append((edge.v, edge.weight, edge))
            adjacency[edge.v].append((edge.u, edge.weight, edge))
        for row in adjacency:
            row.sort(key=lambda item: item[0])
        self._vertex_count = vertex_count
        self._edges = tuple(canonical)
        self._adjacency = tuple(tuple(row) for row in adjacency)

    @property
    def vertex_count(self) -> int:
        return self._vertex_count

    @property
    def edges(self) -> tuple[SpanningEdge, ...]:
        return self._edges

    def neighbors(self, vertex: int) -> tuple[tuple[int, int, SpanningEdge], ...]:
        if vertex < 0 or vertex >= self._vertex_count:
            raise IndexError("vertex out of range")
        return self._adjacency[vertex]


def _safe_add(total: int, weight: int) -> int:
    result = total + weight
    if result < MIN_WEIGHT or result > MAX_WEIGHT:
        raise OverflowError("forest total weight exceeds signed 64-bit range")
    return result


def kruskal_forest(graph: SpanningGraph) -> SpanningForest:
    dsu = DisjointSet(graph.vertex_count)
    accepted: list[SpanningEdge] = []
    events: list[KruskalEvent] = []
    total = 0
    for edge in sorted(graph.edges, key=lambda item: (item.weight, item.u, item.v)):
        before = dsu.component_count
        trace = dsu.union(edge.u, edge.v)
        if trace.merged:
            total = _safe_add(total, edge.weight)
            accepted.append(edge)
        events.append(KruskalEvent(edge, trace.merged, before, dsu.component_count))
    return SpanningForest(tuple(accepted), total, dsu.component_count, tuple(events))


def minimum_spanning_tree(graph: SpanningGraph) -> SpanningForest:
    forest = kruskal_forest(graph)
    if graph.vertex_count == 0 or forest.component_count != 1:
        raise ValueError("graph does not have a spanning tree")
    return forest


def rejected_cycle_edges(graph: SpanningGraph) -> tuple[SpanningEdge, ...]:
    return tuple(event.edge for event in kruskal_forest(graph).events if not event.accepted)


def lazy_prim_forest(graph: SpanningGraph) -> PrimTrace:
    visited = [False] * graph.vertex_count
    accepted: list[SpanningEdge] = []
    starts: list[int] = []
    events: list[PrimEvent] = []
    edge_scans = queue_pushes = stale_pops = max_frontier = 0
    total = 0
    components = 0

    def visit(vertex: int, queue: list[tuple[int, int, int, int, int, SpanningEdge]]) -> None:
        nonlocal edge_scans, queue_pushes, max_frontier
        visited[vertex] = True
        for neighbor, weight, edge in graph.neighbors(vertex):
            edge_scans += 1
            if not visited[neighbor]:
                heapq.heappush(queue, (weight, edge.u, edge.v, vertex, neighbor, edge))
                queue_pushes += 1
                max_frontier = max(max_frontier, len(queue))

    for start in range(graph.vertex_count):
        if visited[start]:
            continue
        components += 1
        starts.append(start)
        queue: list[tuple[int, int, int, int, int, SpanningEdge]] = []
        visit(start, queue)
        while queue:
            _, _, _, from_vertex, to_vertex, edge = heapq.heappop(queue)
            if visited[from_vertex] and visited[to_vertex]:
                stale_pops += 1
                events.append(PrimEvent(edge, False))
                continue
            next_vertex = to_vertex if not visited[to_vertex] else from_vertex
            total = _safe_add(total, edge.weight)
            accepted.append(edge)
            events.append(PrimEvent(edge, True))
            visit(next_vertex, queue)
    forest = SpanningForest(tuple(accepted), total, components, ())
    return PrimTrace(forest, tuple(starts), edge_scans, queue_pushes, stale_pops, max_frontier, tuple(events))


def compare_spanning_forests(graph: SpanningGraph) -> ForestComparison:
    kruskal = kruskal_forest(graph)
    prim = lazy_prim_forest(graph).forest
    expected = graph.vertex_count - kruskal.component_count
    matching = (
        kruskal.total_weight == prim.total_weight
        and kruskal.component_count == prim.component_count
        and len(kruskal.edges) == expected
        and len(prim.edges) == expected
    )
    return ForestComparison(matching, kruskal.total_weight, prim.total_weight, kruskal.component_count, expected)


def sample_spanning_graph() -> SpanningGraph:
    return SpanningGraph(7, (
        (0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5),
        (2, 3, 3), (2, 4, 6), (3, 4, 2), (5, 6, -1),
    ))

