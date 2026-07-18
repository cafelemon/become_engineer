from __future__ import annotations

from dataclasses import dataclass
import heapq


@dataclass(frozen=True)
class Entry:
    priority: int
    sequence: int
    label: str


tasks = (("review", 2), ("test", 1), ("lint", 1), ("deploy", 3))
queue: list[tuple[int, int, Entry]] = []

for sequence, (label, priority) in enumerate(tasks):
    entry = Entry(priority, sequence, label)
    heapq.heappush(queue, (priority, sequence, entry))
    print(f"push {label}@{priority} key=({priority},{sequence})")

print("heap_array=" + ", ".join(f"{item[2].label}@{item[2].priority}" for item in queue))
print("peek=" + f"{queue[0][2].label}@{queue[0][2].priority}")

drained = [heapq.heappop(queue)[2] for _ in range(len(queue))]
print("pop_order=" + ", ".join(f"{entry.label}@{entry.priority}" for entry in drained))
print("tie_sequences=" + ", ".join(str(entry.sequence) for entry in drained if entry.priority == 1))
