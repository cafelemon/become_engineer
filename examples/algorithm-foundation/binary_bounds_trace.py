from dataclasses import dataclass


@dataclass(frozen=True)
class Round:
    left: int
    right: int
    middle: int
    value: int
    next_left: int
    next_right: int


def trace_bound(values: list[int], target: int, *, upper: bool) -> tuple[list[Round], int]:
    left, right = 0, len(values)
    rounds: list[Round] = []
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] <= target if upper else values[middle] < target:
            next_left, next_right = middle + 1, right
        else:
            next_left, next_right = left, middle
        rounds.append(Round(left, right, middle, values[middle], next_left, next_right))
        left, right = next_left, next_right
    return rounds, left


def main() -> None:
    values = [1, 3, 3, 3, 7, 9]
    for name, upper in (("lower", False), ("upper", True)):
        rounds, index = trace_bound(values, 3, upper=upper)
        for number, item in enumerate(rounds, start=1):
            print(
                f"{name} round={number} range=[{item.left},{item.right}) "
                f"mid={item.middle} value={item.value} next=[{item.next_left},{item.next_right})"
            )
        print(f"{name} index={index} comparisons={len(rounds)}")


if __name__ == "__main__":
    main()
