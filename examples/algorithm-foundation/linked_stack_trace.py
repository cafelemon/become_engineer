from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Node:
    value: int
    next: Node | None = None


class LinkedStack:
    def __init__(self) -> None:
        self._top: Node | None = None
        self._size = 0

    def push(self, value: int) -> None:
        self._top = Node(value, self._top)
        self._size += 1

    def pop(self) -> int:
        if self._top is None:
            raise IndexError("pop from empty stack")
        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value

    def peek(self) -> int:
        if self._top is None:
            raise IndexError("peek from empty stack")
        return self._top.value

    def to_list(self) -> list[int]:
        result: list[int] = []
        current = self._top
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def size(self) -> int:
        return self._size


def show(values: LinkedStack) -> str:
    return "[" + ", ".join(str(value) for value in values.to_list()) + "]"


def main() -> None:
    values = LinkedStack()
    values.push(7)
    print(f"push 7  stack={show(values)} size={values.size()}")
    values.push(3)
    print(f"push 3  stack={show(values)} size={values.size()}")
    popped = values.pop()
    print(f"pop -> {popped} stack={show(values)} size={values.size()}")
    values.push(9)
    print(f"push 9  stack={show(values)} size={values.size()}")
    print(f"peek -> {values.peek()} size={values.size()}")


if __name__ == "__main__":
    main()
