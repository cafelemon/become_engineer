GRAPH: dict[int, tuple[int, ...]] = {
    0: (1, 2), 1: (0, 3), 2: (0, 3), 3: (1, 2, 4),
    4: (3,), 5: (6,), 6: (5,),
}

visited: set[int] = set()
components: list[list[int]] = []
first_cycle: tuple[int, int] | None = None


def visit(vertex: int, parent: int | None, depth: int, component: list[int]) -> None:
    global first_cycle
    visited.add(vertex)
    component.append(vertex)
    print(f"{'  ' * depth}enter={vertex} parent={parent} depth={depth}")
    for neighbor in GRAPH[vertex]:
        print(f"{'  ' * depth}check={vertex}-{neighbor}")
        if neighbor not in visited:
            visit(neighbor, vertex, depth + 1, component)
        elif neighbor != parent and first_cycle is None:
            first_cycle = (min(vertex, neighbor), max(vertex, neighbor))
            print(f"{'  ' * depth}cycle_edge={first_cycle}")


for candidate in range(len(GRAPH)):
    if candidate in visited:
        continue
    component: list[int] = []
    print(f"start_component={candidate}")
    visit(candidate, None, 0, component)
    components.append(component)

labels = [-1] * len(GRAPH)
for label, component in enumerate(components):
    for vertex in component:
        labels[vertex] = label

print(f"components={components}")
print(f"first_cycle={first_cycle}")
print(f"labels={labels}")
