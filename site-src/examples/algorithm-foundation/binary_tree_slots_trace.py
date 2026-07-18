from __future__ import annotations


def normalize_slots(values: list[int | None]) -> tuple[int | None, ...]:
    slots = list(values)
    if slots and slots[0] is None:
        raise ValueError("non-empty tree requires a root value")
    while slots and slots[-1] is None:
        slots.pop()
    for index, value in enumerate(slots[1:], start=1):
        parent = (index - 1) // 2
        if value is not None and slots[parent] is None:
            raise ValueError(f"slot {index} has no parent")
    return tuple(slots)


def path_to_slot(slots: tuple[int | None, ...], index: int) -> tuple[int, str]:
    if index < 0 or index >= len(slots):
        raise IndexError("slot index out of range")
    value = slots[index]
    if value is None:
        raise IndexError("slot is empty")
    directions: list[str] = []
    cursor = index
    while cursor > 0:
        directions.append("L" if cursor % 2 == 1 else "R")
        cursor = (cursor - 1) // 2
    return value, "".join(reversed(directions)) or "root"


def main() -> None:
    slots = normalize_slots([7, 3, 9, None, 5, 8, 11, None, None])
    print("slots=[7,3,9,null,5,8,11]")
    for index in (0, 4, 6):
        value, path = path_to_slot(slots, index)
        parent = "none" if index == 0 else str((index - 1) // 2)
        print(f"index={index} value={value} path={path} parent={parent}")
    for label, values in (("orphan", [7, None, 9, 4]), ("empty_root", [None])):
        try:
            normalize_slots(values)
        except ValueError as error:
            print(f"{label}=rejected reason={error}")
    try:
        path_to_slot(slots, 3)
    except IndexError as error:
        print(f"empty_slot=3 rejected reason={error}")


if __name__ == "__main__":
    main()
