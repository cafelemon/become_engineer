from __future__ import annotations


parents = [0, 0, 0, 0, 0, 4, 4]
sizes = [7, 1, 2, 1, 3, 1, 1]


def find(element: int) -> tuple[int, tuple[int, ...], int]:
    path = [element]
    current = element
    while parents[current] != current:
        current = parents[current]
        path.append(current)
    root = current
    compressions = 0
    for item in path[:-1]:
        if parents[item] != root:
            parents[item] = root
            compressions += 1
    return root, tuple(path), compressions


print("parents_before=" + ",".join(map(str, parents)))
root, path, compressions = find(5)
print("path=" + "->".join(map(str, path)))
print(f"root={root} visits={len(path)} compressions={compressions}")
print("parents_after=" + ",".join(map(str, parents)))
print(f"root_size={sizes[root]}")

