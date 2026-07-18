from __future__ import annotations

import heapq


edges = ((0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 3), (2, 4, 6), (3, 4, 2), (5, 6, -1))
adjacency: list[list[tuple[int, int, int, int]]] = [[] for _ in range(7)]
for first, second, weight in edges:
    u, v = min(first, second), max(first, second)
    adjacency[u].append((v, weight, u, v))
    adjacency[v].append((u, weight, u, v))
for row in adjacency:
    row.sort(key=lambda item: item[0])

visited = [False] * 7
starts: list[int] = []
accepted: list[tuple[int, int, int]] = []
edge_scans = queue_pushes = stale_pops = max_frontier = total_weight = 0


def visit(vertex: int, queue: list[tuple[int, int, int, int, int]]) -> None:
    global edge_scans, queue_pushes, max_frontier
    visited[vertex] = True
    for neighbor, weight, u, v in adjacency[vertex]:
        edge_scans += 1
        if not visited[neighbor]:
            heapq.heappush(queue, (weight, u, v, vertex, neighbor))
            queue_pushes += 1
            max_frontier = max(max_frontier, len(queue))


for start in range(7):
    if visited[start]:
        continue
    starts.append(start)
    print(f"start {start}")
    frontier: list[tuple[int, int, int, int, int]] = []
    visit(start, frontier)
    while frontier:
        weight, u, v, from_vertex, to_vertex = heapq.heappop(frontier)
        if visited[from_vertex] and visited[to_vertex]:
            stale_pops += 1
            print(f"stale {u}-{v}@{weight}")
            continue
        next_vertex = to_vertex if not visited[to_vertex] else from_vertex
        total_weight += weight
        accepted.append((u, v, weight))
        print(f"accept {u}-{v}@{weight} next={next_vertex}")
        visit(next_vertex, frontier)

print(
    f"starts={','.join(map(str, starts))} scans={edge_scans} pushes={queue_pushes} "
    f"stale={stale_pops} max_frontier={max_frontier} total_weight={total_weight} components={len(starts)}"
)
