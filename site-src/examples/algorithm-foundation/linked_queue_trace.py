from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Node:
    value: int
    next: Node | None = None


class LinkedQueue:
    def __init__(self) -> None:
        self._head: Node | None = None
        self._tail: Node | None = None
        self._size = 0

    def enqueue(self, value: int) -> None:
        node = Node(value)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def dequeue(self) -> int:
        if self._head is None:
            raise IndexError("dequeue from empty queue")
        value = self._head.value
        self._head = self._head.next
        self._size -= 1
        if self._head is None:
            self._tail = None
        return value

    def endpoints(self) -> tuple[int | None, int | None]:
        front = None if self._head is None else self._head.value
        back = None if self._tail is None else self._tail.value
        return front, back

    def size(self) -> int:
        return self._size


def show(queue: LinkedQueue, action: str) -> None:
    front, back = queue.endpoints()
    print(f"{action:<12} front={front} back={back} size={queue.size()}")


def main() -> None:
    queue = LinkedQueue()
    show(queue, "empty")
    queue.enqueue(7)
    show(queue, "enqueue 7")
    queue.enqueue(3)
    show(queue, "enqueue 3")
    print(f"dequeue -> {queue.dequeue()}")
    show(queue, "after first")
    print(f"dequeue -> {queue.dequeue()}")
    show(queue, "empty again")
    queue.enqueue(9)
    show(queue, "reuse 9")


if __name__ == "__main__":
    main()
