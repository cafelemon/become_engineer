from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Node:
    value: int
    next: Node | None = None


class SinglyLinkedList:
    def __init__(self) -> None:
        self._head: Node | None = None
        self._size = 0

    def append(self, value: int) -> None:
        new_node = Node(value)
        if self._head is None:
            self._head = new_node
        else:
            current = self._head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def find(self, value: int) -> tuple[int | None, int]:
        current = self._head
        visits = 0
        while current is not None:
            visits += 1
            if current.value == value:
                return visits - 1, visits
            current = current.next
        return None, visits

    def pop_front(self) -> int:
        if self._head is None:
            raise IndexError("pop_front from empty linked list")
        value = self._head.value
        self._head = self._head.next
        self._size -= 1
        return value

    def to_list(self) -> list[int]:
        result: list[int] = []
        current = self._head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def size(self) -> int:
        return self._size


def main() -> None:
    values = SinglyLinkedList()
    for value in (7, 3, 9):
        values.append(value)

    index, visits = values.find(3)
    print("linked=" + " -> ".join(str(value) for value in values.to_list()))
    print(f"find=3 index={index} visits={visits}")
    print(f"pop_front={values.pop_front()}")
    print("remaining=" + " -> ".join(str(value) for value in values.to_list()))
    print(f"size={values.size()}")


if __name__ == "__main__":
    main()
