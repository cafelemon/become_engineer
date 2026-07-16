from __future__ import annotations

from .graph import degree_sequence, describe_graph, sample_graph
from .traversal import breadth_first, build_component_labels, depth_first_components, shortest_path


def _join(values: tuple[int, ...]) -> str:
    return ", ".join(str(value) for value in values)


def build_graph_report() -> str:
    graph = sample_graph()
    summary = describe_graph(graph)
    rows = [
        "可追踪无向图实验",
        f"vertices={summary.vertex_count}，edges={summary.edge_count}，adjacency_entries={summary.adjacency_entries}",
    ]
    rows.extend(f"{vertex}：[{_join(graph.neighbors(vertex))}]" for vertex in range(graph.vertex_count))
    rows.append(f"degrees：{_join(degree_sequence(graph))}")
    return "\n".join(rows)


def build_bfs_report() -> str:
    graph = sample_graph()
    trace = breadth_first(graph, 0)
    path = shortest_path(graph, 0, 4)
    distances = ", ".join("unreachable" if value is None else str(value) for value in trace.distances)
    parents = ", ".join("none" if value is None else str(value) for value in trace.parents)
    return "\n".join(
        (
            "无权图 BFS",
            "start=0",
            f"order：{_join(trace.order)}",
            f"distances：{distances}",
            f"parents：{parents}",
            f"visits={trace.visits}，edge_checks={trace.edge_checks}，max_frontier={trace.max_frontier}",
            f"path 0->4：{_join(path.path)}，distance={path.distance}",
        )
    )


def build_dfs_report() -> str:
    graph = sample_graph()
    trace = depth_first_components(graph)
    labels = build_component_labels(graph)
    rows = ["全图 DFS", f"components={len(trace.components)}"]
    rows.extend(f"component {index}：{_join(component)}" for index, component in enumerate(trace.components))
    rows.append(f"visits={trace.visits}，edge_checks={trace.edge_checks}，max_depth={trace.max_depth}")
    cycle = "no" if trace.cycle_edge is None else "yes"
    edge = "none" if trace.cycle_edge is None else f"({trace.cycle_edge.u}, {trace.cycle_edge.v})"
    rows.append(f"cycle={cycle}，first_edge={edge}")
    rows.append(f"labels：{_join(labels.labels)}")
    return "\n".join(rows)
