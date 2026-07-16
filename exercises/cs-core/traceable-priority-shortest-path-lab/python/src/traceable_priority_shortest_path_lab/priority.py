from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class PriorityEntry:
    priority: int
    sequence: int
    label: str


@dataclass(frozen=True, slots=True)
class PriorityMutation:
    entry: PriorityEntry
    comparisons: int
    swaps: int
    entries: tuple[PriorityEntry, ...]


@dataclass(frozen=True, slots=True)
class PriorityPop:
    entry: PriorityEntry
    comparisons: int
    swaps: int
    entries: tuple[PriorityEntry, ...]


def _less(left: PriorityEntry, right: PriorityEntry) -> bool:
    return (left.priority, left.sequence) < (right.priority, right.sequence)


class StableMinPriorityQueue:
    def __init__(self) -> None:
        self._entries: list[PriorityEntry] = []
        self._next_sequence = 0

    @property
    def entries(self) -> tuple[PriorityEntry, ...]:
        return tuple(self._entries)

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def empty(self) -> bool:
        return not self._entries

    def push(self, label: str, priority: int) -> PriorityMutation:
        entry = PriorityEntry(priority, self._next_sequence, label)
        self._next_sequence += 1
        self._entries.append(entry)
        index = len(self._entries) - 1
        comparisons = 0
        swaps = 0
        while index > 0:
            parent = (index - 1) // 2
            comparisons += 1
            if not _less(self._entries[index], self._entries[parent]):
                break
            self._entries[index], self._entries[parent] = self._entries[parent], self._entries[index]
            swaps += 1
            index = parent
        return PriorityMutation(entry, comparisons, swaps, self.entries)

    def peek(self) -> PriorityEntry:
        if not self._entries:
            raise IndexError("peek from empty priority queue")
        return self._entries[0]

    def pop(self) -> PriorityPop:
        if not self._entries:
            raise IndexError("pop from empty priority queue")
        entry = self._entries[0]
        last = self._entries.pop()
        comparisons = 0
        swaps = 0
        if self._entries:
            self._entries[0] = last
            index = 0
            while True:
                left = index * 2 + 1
                if left >= len(self._entries):
                    break
                right = left + 1
                child = left
                if right < len(self._entries):
                    comparisons += 1
                    if _less(self._entries[right], self._entries[left]):
                        child = right
                comparisons += 1
                if not _less(self._entries[child], self._entries[index]):
                    break
                self._entries[index], self._entries[child] = self._entries[child], self._entries[index]
                swaps += 1
                index = child
        return PriorityPop(entry, comparisons, swaps, self.entries)


def drain_by_priority(tasks: Sequence[tuple[str, int]]) -> tuple[PriorityEntry, ...]:
    queue = StableMinPriorityQueue()
    for label, priority in tasks:
        queue.push(label, priority)
    drained: list[PriorityEntry] = []
    while not queue.empty:
        drained.append(queue.pop().entry)
    return tuple(drained)
