from __future__ import annotations

import heapq


adjacency = (
    ((1, 4), (2, 1)),
    ((0, 4), (2, 2), (3, 1), (4, 7)),
    ((0, 1), (1, 2), (3, 5)),
    ((1, 1), (2, 5), (4, 3)),
    ((1, 7), (3, 3), (5, 1)),
    ((4, 1),),
    (),
)

distances: list[int | None] = [None] * len(adjacency)
parents: list[int | None] = [None] * len(adjacency)
distances[0] = 0
frontier: list[tuple[int, int, int]] = [(0, 0, 0)]
sequence = 1
settled: list[int] = []
stale_pops = 0

while frontier:
    distance, _, vertex = heapq.heappop(frontier)
    if distances[vertex] != distance:
        stale_pops += 1
        print(f"stale vertex={vertex} queued={distance} current={distances[vertex]}")
        continue
    settled.append(vertex)
    for neighbor, weight in adjacency[vertex]:
        candidate = distance + weight
        old = distances[neighbor]
        if old is None or candidate < old:
            distances[neighbor] = candidate
            parents[neighbor] = vertex
            heapq.heappush(frontier, (candidate, sequence, neighbor))
            sequence += 1
            print(f"relax {vertex}->{neighbor}: {old}->{candidate}")

print("settled=" + ",".join(map(str, settled)))
print("distances=" + ",".join("unreachable" if value is None else str(value) for value in distances))
print(f"stale_pops={stale_pops}")

