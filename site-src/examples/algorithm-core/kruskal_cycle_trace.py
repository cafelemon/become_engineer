from __future__ import annotations


edges = ((0, 1, 4), (0, 2, 1), (1, 2, 2), (1, 3, 5), (2, 3, 3), (2, 4, 6), (3, 4, 2), (5, 6, -1))
parents = list(range(7))
sizes = [1] * 7
components = 7
total = 0


def find(element: int) -> int:
    while parents[element] != element:
        element = parents[element]
    return element


for u, v, weight in sorted(edges, key=lambda edge: (edge[2], edge[0], edge[1])):
    first, second = find(u), find(v)
    if first == second:
        print(f"reject {u}-{v}@{weight} same_root={first}")
        continue
    if (sizes[first], -first) < (sizes[second], -second):
        first, second = second, first
    parents[second] = first
    sizes[first] += sizes[second]
    components -= 1
    total += weight
    print(f"accept {u}-{v}@{weight} components={components}")

print(f"total_weight={total} components={components} edge_count={7-components}")

