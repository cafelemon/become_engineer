from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FindTrace:
    root: int
    path: tuple[int, ...]
    visits: int
    compressions: int


@dataclass(frozen=True, slots=True)
class UnionTrace:
    merged: bool
    root: int
    attached_root: int | None
    component_count: int
    find_visits: int
    compressions: int


@dataclass(frozen=True, slots=True)
class ComponentGroup:
    representative: int
    members: tuple[int, ...]


class DisjointSet:
    def __init__(self, element_count: int) -> None:
        if element_count < 0:
            raise ValueError("element_count must be non-negative")
        self._parents = list(range(element_count))
        self._sizes = [1] * element_count
        self._component_count = element_count

    def _check(self, element: int) -> None:
        if element < 0 or element >= len(self._parents):
            raise IndexError("element out of range")

    def find(self, element: int) -> FindTrace:
        self._check(element)
        path = [element]
        current = element
        while self._parents[current] != current:
            current = self._parents[current]
            path.append(current)
        root = current
        compressions = 0
        for item in path[:-1]:
            if self._parents[item] != root:
                self._parents[item] = root
                compressions += 1
        return FindTrace(root, tuple(path), len(path), compressions)

    def union(self, first: int, second: int) -> UnionTrace:
        first_trace = self.find(first)
        second_trace = self.find(second)
        visits = first_trace.visits + second_trace.visits
        compressions = first_trace.compressions + second_trace.compressions
        first_root = first_trace.root
        second_root = second_trace.root
        if first_root == second_root:
            return UnionTrace(False, first_root, None, self._component_count, visits, compressions)
        if (self._sizes[first_root], -first_root) < (self._sizes[second_root], -second_root):
            first_root, second_root = second_root, first_root
        self._parents[second_root] = first_root
        self._sizes[first_root] += self._sizes[second_root]
        self._component_count -= 1
        return UnionTrace(True, first_root, second_root, self._component_count, visits, compressions)

    def connected(self, first: int, second: int) -> bool:
        return self.find(first).root == self.find(second).root

    @property
    def parents(self) -> tuple[int, ...]:
        return tuple(self._parents)

    @property
    def sizes(self) -> tuple[int, ...]:
        return tuple(self._sizes)

    @property
    def component_count(self) -> int:
        return self._component_count

    def groups(self) -> tuple[ComponentGroup, ...]:
        grouped: dict[int, list[int]] = {}
        for element in range(len(self._parents)):
            root = self.find(element).root
            grouped.setdefault(root, []).append(element)
        return tuple(ComponentGroup(root, tuple(grouped[root])) for root in sorted(grouped))

