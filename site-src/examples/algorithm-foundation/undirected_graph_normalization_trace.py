from __future__ import annotations


def normalize(vertex_count: int, edges: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    canonical: list[tuple[int, int]] = []
    for left, right in edges:
        if not (0 <= left < vertex_count and 0 <= right < vertex_count):
            raise ValueError("edge endpoint out of range")
        if left == right:
            raise ValueError("self-loop is not allowed")
        canonical.append((min(left, right), max(left, right)))
    canonical.sort()
    if len(canonical) != len(set(canonical)):
        raise ValueError("duplicate undirected edge")
    return tuple(canonical)


def main() -> None:
    edges = normalize(5, [(3, 1), (2, 0), (4, 3)])
    print(f"canonical={list(edges)}")
    adjacency = [[] for _ in range(5)]
    for left, right in edges:
        adjacency[left].append(right); adjacency[right].append(left)
    for vertex, neighbors in enumerate(adjacency):
        print(f"vertex={vertex} neighbors={neighbors} degree={len(neighbors)}")
    print(f"degree_sum={sum(map(len, adjacency))} twice_edges={2 * len(edges)}")
    for label, bad in (("self_loop", [(1, 1)]), ("reverse_duplicate", [(0, 2), (2, 0)])):
        try: normalize(3, bad)
        except ValueError as error: print(f"{label}=rejected reason={error}")


if __name__ == "__main__": main()
