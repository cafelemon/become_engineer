from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FindTrace:
    index: int | None
    visits: int


class _Node:
    __slots__ = ("value", "next")

    def __init__(self, value: int, next_node: _Node | None = None) -> None:
        self.value = value
        self.next = next_node


class SinglyLinkedList:
    def __init__(self, values: Iterable[int] = ()) -> None:
        self._head: _Node | None = None
        self._size = 0
        for value in values:
            self.append(value)

    def push_front(self, value: int) -> None:
        self._head = _Node(value, self._head)
        self._size += 1

    def append(self, value: int) -> None:
        new_node = _Node(value)
        if self._head is None:
            self._head = new_node
        else:
            current = self._head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def pop_front(self) -> int:
        if self._head is None:
            raise IndexError("pop_front from empty linked list")
        value = self._head.value
        self._head = self._head.next
        self._size -= 1
        return value

    def find(self, value: int) -> FindTrace:
        current = self._head
        visits = 0
        while current is not None:
            visits += 1
            if current.value == value:
                return FindTrace(visits - 1, visits)
            current = current.next
        return FindTrace(None, visits)

    def remove_first(self, value: int) -> bool:
        previous: _Node | None = None
        current = self._head
        while current is not None:
            if current.value == value:
                if previous is None:
                    self._head = current.next
                else:
                    previous.next = current.next
                self._size -= 1
                return True
            previous = current
            current = current.next
        return False

    def to_list(self) -> list[int]:
        result: list[int] = []
        current = self._head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def size(self) -> int:
        return self._size

    def empty(self) -> bool:
        return self._head is None


class _StackNode:
    __slots__ = ("value", "next")

    def __init__(self, value: int, next_node: _StackNode | None = None) -> None:
        self.value = value
        self.next = next_node


class LinkedStack:
    def __init__(self, values: Iterable[int] = ()) -> None:
        self._head: _StackNode | None = None
        self._size = 0
        for value in values:
            self.push(value)

    def push(self, value: int) -> None:
        self._head = _StackNode(value, self._head)
        self._size += 1

    def pop(self) -> int:
        if self._head is None:
            raise IndexError("pop from empty stack")
        value = self._head.value
        self._head = self._head.next
        self._size -= 1
        return value

    def peek(self) -> int:
        if self._head is None:
            raise IndexError("peek from empty stack")
        return self._head.value

    def to_list(self) -> list[int]:
        result: list[int] = []
        current = self._head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def size(self) -> int:
        return self._size

    def empty(self) -> bool:
        return self._head is None


class _QueueNode:
    __slots__ = ("value", "next")

    def __init__(self, value: int) -> None:
        self.value = value
        self.next: _QueueNode | None = None


class LinkedQueue:
    def __init__(self, values: Iterable[int] = ()) -> None:
        self._head: _QueueNode | None = None
        self._tail: _QueueNode | None = None
        self._size = 0
        for value in values:
            self.enqueue(value)

    def enqueue(self, value: int) -> None:
        new_node = _QueueNode(value)
        if self._tail is None:
            self._head = new_node
        else:
            self._tail.next = new_node
        self._tail = new_node
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

    def front(self) -> int:
        if self._head is None:
            raise IndexError("front from empty queue")
        return self._head.value

    def back(self) -> int:
        if self._tail is None:
            raise IndexError("back from empty queue")
        return self._tail.value

    def to_list(self) -> list[int]:
        result: list[int] = []
        current = self._head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def size(self) -> int:
        return self._size

    def empty(self) -> bool:
        return self._head is None


def drain_stack(values: Iterable[int]) -> list[int]:
    stack = LinkedStack(values)
    result: list[int] = []
    while not stack.empty():
        result.append(stack.pop())
    return result


def serve_until_empty(values: Iterable[int]) -> list[int]:
    queue = LinkedQueue(values)
    result: list[int] = []
    while not queue.empty():
        result.append(queue.dequeue())
    return result
