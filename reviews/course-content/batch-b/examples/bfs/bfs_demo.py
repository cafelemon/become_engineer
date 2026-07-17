from collections import deque


def shortest_path(graph: dict[str, list[str]], start: str, target: str) -> list[str]:
    queue = deque([start])
    parent: dict[str, str | None] = {start: None}
    while queue:
        current = queue.popleft()
        if current == target:
            break
        for neighbor in graph[current]:
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)
    if target not in parent:
        return []
    path: list[str] = []
    cursor: str | None = target
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    return list(reversed(path))


GRAPH = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
    "F": [],
}

print("path A->E:", " -> ".join(shortest_path(GRAPH, "A", "E")))
print("path A->F:", shortest_path(GRAPH, "A", "F"))
