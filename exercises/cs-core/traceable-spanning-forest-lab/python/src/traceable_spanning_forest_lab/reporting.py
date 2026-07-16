from __future__ import annotations

from .dsu import DisjointSet
from .forest import SpanningEdge, compare_spanning_forests, kruskal_forest, lazy_prim_forest, sample_spanning_graph


def _edges(values: tuple[SpanningEdge, ...]) -> str:
    return ", ".join(f"{edge.u}-{edge.v}@{edge.weight}" for edge in values)


def build_dsu_report() -> str:
    dsu = DisjointSet(7)
    merged = 0
    for first, second in ((0, 1), (2, 3), (0, 2), (4, 5), (5, 6), (3, 6)):
        merged += int(dsu.union(first, second).merged)
    before = dsu.parents
    trace = dsu.find(5)
    return "\n".join((
        "可追踪并查集",
        "elements=7",
        "unions：0-1, 2-3, 0-2, 4-5, 5-6, 3-6",
        f"merged={merged}，components={dsu.component_count}",
        f"parents_before_find：{', '.join(map(str, before))}",
        f"find(5)：root={trace.root}，visits={trace.visits}，compressed={trace.compressions}",
        f"parents_after_find：{', '.join(map(str, dsu.parents))}",
        f"connected(3,6)={'yes' if dsu.connected(3, 6) else 'no'}",
    ))


def build_kruskal_report() -> str:
    graph = sample_spanning_graph()
    forest = kruskal_forest(graph)
    ordered = tuple(sorted(graph.edges, key=lambda edge: (edge.weight, edge.u, edge.v)))
    rejected = sum(not event.accepted for event in forest.events)
    return "\n".join((
        "Kruskal 最小生成森林",
        f"edges_sorted：{_edges(ordered)}",
        f"accepted：{_edges(forest.edges)}",
        f"rejected_cycles={rejected}，components={forest.component_count}",
        f"total_weight={forest.total_weight}，edge_count={len(forest.edges)}",
    ))


def build_prim_report() -> str:
    graph = sample_spanning_graph()
    trace = lazy_prim_forest(graph)
    comparison = compare_spanning_forests(graph)
    return "\n".join((
        "Lazy Prim 最小生成森林",
        f"component_starts：{', '.join(map(str, trace.component_starts))}",
        f"accepted：{_edges(trace.forest.edges)}",
        f"edge_scans={trace.edge_scans}，queue_pushes={trace.queue_pushes}，stale_pops={trace.stale_pops}，max_frontier={trace.max_frontier}",
        f"components={trace.forest.component_count}，total_weight={trace.forest.total_weight}",
        f"matches_kruskal={'yes' if comparison.matching else 'no'}",
    ))
