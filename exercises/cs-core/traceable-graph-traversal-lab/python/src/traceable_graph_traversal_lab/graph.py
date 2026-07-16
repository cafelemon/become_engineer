from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True, order=True, slots=True)
class Edge:
    u: int
    v: int


@dataclass(frozen=True, slots=True)
class GraphSummary:
    vertex_count: int
    edge_count: int
    adjacency_entries: int


class UndirectedGraph:
    """A validated simple undirected graph with deterministic neighbor order."""

    def __init__(self, vertex_count: int, edges: Iterable[tuple[int, int] | Edge]) -> None:
        if vertex_count < 0:
            raise ValueError("vertex_count must be non-negative")
        canonical: list[Edge] = []
        seen: set[Edge] = set()
        for raw_edge in edges:
            u, v = (raw_edge.u, raw_edge.v) if isinstance(raw_edge, Edge) else raw_edge
            if u < 0 or v < 0 or u >= vertex_count or v >= vertex_count:
                raise ValueError("edge endpoint out of range")
            if u == v:
                raise ValueError("self-loops are not allowed")
            edge = Edge(min(u, v), max(u, v))
            if edge in seen:
                raise ValueError("duplicate edges are not allowed")
            seen.add(edge)
            canonical.append(edge)

        canonical.sort()
        adjacency: list[list[int]] = [[] for _ in range(vertex_count)]
        for edge in canonical:
            adjacency[edge.u].append(edge.v)
            adjacency[edge.v].append(edge.u)
        for neighbors in adjacency:
            neighbors.sort()

        self._vertex_count = vertex_count
        self._edges = tuple(canonical)
        self._adjacency = tuple(tuple(neighbors) for neighbors in adjacency)

    @property
    def vertex_count(self) -> int:
        return self._vertex_count

    @property
    def edges(self) -> tuple[Edge, ...]:
        return self._edges

    def neighbors(self, vertex: int) -> tuple[int, ...]:
        self._check_vertex(vertex)
        return self._adjacency[vertex]

    def _check_vertex(self, vertex: int) -> None:
        if vertex < 0 or vertex >= self._vertex_count:
            raise IndexError("vertex out of range")


def describe_graph(graph: UndirectedGraph) -> GraphSummary:
    return GraphSummary(graph.vertex_count, len(graph.edges), len(graph.edges) * 2)


def build_adjacency_matrix(graph: UndirectedGraph) -> tuple[tuple[bool, ...], ...]:
    matrix = [[False] * graph.vertex_count for _ in range(graph.vertex_count)]
    for edge in graph.edges:
        matrix[edge.u][edge.v] = True
        matrix[edge.v][edge.u] = True
    return tuple(tuple(row) for row in matrix)


def degree_sequence(graph: UndirectedGraph) -> tuple[int, ...]:
    return tuple(len(graph.neighbors(vertex)) for vertex in range(graph.vertex_count))


def has_edge(graph: UndirectedGraph, u: int, v: int) -> bool:
    graph._check_vertex(u)
    graph._check_vertex(v)
    return v in graph.neighbors(u)


def sample_graph() -> UndirectedGraph:
    edges: Sequence[tuple[int, int]] = ((0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (5, 6))
    return UndirectedGraph(7, edges)
