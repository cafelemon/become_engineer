from collections import deque


GRAPH: dict[int, tuple[int, ...]] = {
    0: (1, 2), 1: (0, 3), 2: (0, 3), 3: (1, 2, 4),
    4: (3,), 5: (6,), 6: (5,),
}


def bfs(start: int) -> tuple[list[int], list[int | None], list[int | None]]:
    queue = deque([start])
    distances: list[int | None] = [None] * len(GRAPH)
    parents: list[int | None] = [None] * len(GRAPH)
    distances[start] = 0
    order: list[int] = []
    while queue:
        current = queue.popleft()
        order.append(current)
        print(f"pop={current} queue={list(queue)}")
        for neighbor in GRAPH[current]:
            if distances[neighbor] is not None:
                continue
            current_distance = distances[current]
            assert current_distance is not None
            distances[neighbor] = current_distance + 1
            parents[neighbor] = current
            queue.append(neighbor)
            print(f"  discover={neighbor} distance={distances[neighbor]} parent={current} queue={list(queue)}")
    return order, distances, parents


def restore_path(start: int, target: int, distances: list[int | None], parents: list[int | None]) -> list[int]:
    if distances[target] is None:
        return []
    path: list[int] = []
    cursor: int | None = target
    while cursor is not None:
        path.append(cursor)
        if cursor == start:
            break
        cursor = parents[cursor]
    path.reverse()
    return path


order, distances, parents = bfs(0)
print(f"order={order}")
print(f"distances={distances}")
print(f"parents={parents}")
print(f"path_0_4={restore_path(0, 4, distances, parents)}")
print(f"path_0_6={restore_path(0, 6, distances, parents)}")
