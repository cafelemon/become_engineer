from dataclasses import dataclass
from collections.abc import Sequence


@dataclass(frozen=True)
class CapacityEvent:
    value: int
    size: int
    capacity: int
    copies: int
    steps: int


def simulate_growth(
    values: Sequence[int], initial_capacity: int = 0
) -> list[CapacityEvent]:
    if initial_capacity < 0:
        raise ValueError("initial_capacity must not be negative")

    size = 0
    capacity = initial_capacity
    events: list[CapacityEvent] = []
    for value in values:
        copies = 0
        if size == capacity:
            copies = size
            capacity = 1 if capacity == 0 else capacity * 2
        size += 1
        events.append(CapacityEvent(value, size, capacity, copies, copies + 1))
    return events


def main() -> None:
    events = simulate_growth([7, 3, 9, 3, 5])
    print("append | size | capacity | copies | steps")
    for event in events:
        print(
            f"{event.value} | {event.size} | {event.capacity} | "
            f"{event.copies} | {event.steps}"
        )
    print(f"total_steps={sum(event.steps for event in events)}")


if __name__ == "__main__":
    main()
