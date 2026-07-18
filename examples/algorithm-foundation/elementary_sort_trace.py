from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    key: int
    tag: str


def show(items: list[Item]) -> str:
    return ",".join(f"{item.key}{item.tag}" for item in items)


def insertion(values: list[Item]) -> None:
    items = list(values)
    comparisons = shifts = 0
    for current_index in range(1, len(items)):
        current = items[current_index]
        position = current_index
        while position > 0:
            comparisons += 1
            if current.key >= items[position - 1].key:
                break
            items[position] = items[position - 1]
            shifts += 1
            position -= 1
        items[position] = current
        print(f"insertion pass={current_index} items=[{show(items)}] comparisons={comparisons} shifts={shifts}")


def selection(values: list[Item]) -> None:
    items = list(values)
    comparisons = swaps = 0
    for start in range(len(items) - 1):
        selected = start
        for candidate in range(start + 1, len(items)):
            comparisons += 1
            if items[candidate].key < items[selected].key:
                selected = candidate
        if selected != start:
            items[start], items[selected] = items[selected], items[start]
            swaps += 1
        print(f"selection pass={start + 1} items=[{show(items)}] comparisons={comparisons} swaps={swaps}")


def main() -> None:
    values = [Item(3, "A"), Item(1, "B"), Item(3, "C"), Item(2, "D")]
    print(f"input=[{show(values)}]")
    insertion(values)
    selection(values)


if __name__ == "__main__":
    main()
