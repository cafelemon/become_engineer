from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    key: int
    tag: str


def show(items: list[Item]) -> str:
    return ",".join(f"{item.key}{item.tag}" for item in items)


def merge(left: list[Item], right: list[Item]) -> tuple[list[Item], int]:
    result: list[Item] = []
    left_index = right_index = comparisons = 0
    while left_index < len(left) and right_index < len(right):
        comparisons += 1
        if right[right_index].key < left[left_index].key:
            result.append(right[right_index]); right_index += 1
        else:
            result.append(left[left_index]); left_index += 1
    result.extend(left[left_index:]); result.extend(right[right_index:])
    return result, comparisons


def main() -> None:
    items = [Item(3, "A"), Item(1, "B"), Item(3, "C"), Item(2, "D")]
    width = 1
    comparisons = writes = 0
    print(f"input=[{show(items)}]")
    while width < len(items):
        next_items: list[Item] = []
        groups: list[str] = []
        for start in range(0, len(items), width * 2):
            merged, count = merge(items[start:start + width], items[start + width:start + width * 2])
            next_items.extend(merged); groups.append(show(merged))
            comparisons += count; writes += len(merged)
        items = next_items
        print(f"width={width} groups=[{' | '.join(groups)}] comparisons={comparisons} writes={writes}")
        width *= 2
    print(f"result=[{show(items)}] stable=yes")


if __name__ == "__main__":
    main()
