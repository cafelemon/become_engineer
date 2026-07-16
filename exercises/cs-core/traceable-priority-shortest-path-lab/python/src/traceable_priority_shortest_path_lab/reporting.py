from __future__ import annotations

from .heap import TraceableMinHeap
from .priority import StableMinPriorityQueue
from .weighted import dijkstra, sample_weighted_graph, shortest_path


def _join(values: tuple[int, ...]) -> str:
    return ", ".join(str(value) for value in values)


def build_heap_report() -> str:
    heap = TraceableMinHeap()
    comparisons = 0
    swaps = 0
    for value in (7, 3, 9, 1, 5):
        event = heap.push(value)
        comparisons += event.comparisons
        swaps += event.swaps
    values = heap.values
    popped = heap.pop_min()
    return "\n".join((
        "可追踪最小堆",
        "push：7, 3, 9, 1, 5",
        f"heap：{_join(values)}",
        f"comparisons={comparisons}，swaps={swaps}",
        f"pop_min={popped.value}",
        f"remaining：{_join(popped.values)}",
        f"pop_comparisons={popped.comparisons}，pop_swaps={popped.swaps}",
    ))


def build_queue_report() -> str:
    queue = StableMinPriorityQueue()
    tasks = (("review", 2), ("test", 1), ("lint", 1), ("deploy", 3))
    for label, priority in tasks:
        queue.push(label, priority)
    heap_array = ", ".join(f"{entry.label}@{entry.priority}" for entry in queue.entries)
    peek = queue.peek()
    popped = []
    while not queue.empty:
        entry = queue.pop().entry
        popped.append(f"{entry.label}@{entry.priority}")
    return "\n".join((
        "稳定优先队列",
        "push：review@2, test@1, lint@1, deploy@3",
        f"heap_array：{heap_array}",
        f"peek：{peek.label}@{peek.priority}",
        f"pop_order：{', '.join(popped)}",
        "equal_priority_fifo=yes",
    ))


def build_dijkstra_report() -> str:
    graph = sample_weighted_graph()
    trace = dijkstra(graph, 0)
    path = shortest_path(graph, 0, 5)
    distances = ", ".join("unreachable" if value is None else str(value) for value in trace.distances)
    parents = ", ".join("none" if value is None else str(value) for value in trace.parents)
    return "\n".join((
        "非负权最短路",
        "start=0",
        f"settled：{_join(trace.settled)}",
        f"distances：{distances}",
        f"parents：{parents}",
        f"edge_checks={trace.edge_checks}，relaxations={trace.relaxations}",
        f"queue_pushes={trace.queue_pushes}，stale_pops={trace.stale_pops}，max_frontier={trace.max_frontier}",
        f"path 0->5：{_join(path.path)}，distance={path.distance}",
    ))
