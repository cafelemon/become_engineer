from dataclasses import dataclass


@dataclass(frozen=True)
class ScanEvent:
    visit: int
    value: int
    repeated: bool
    unique: tuple[int, ...]


def trace(values: list[int]) -> tuple[list[ScanEvent], list[tuple[int, int]]]:
    seen: set[int] = set()
    unique: list[int] = []
    counts: dict[int, int] = {}
    events: list[ScanEvent] = []
    for visit, value in enumerate(values, start=1):
        repeated = value in seen
        if not repeated:
            seen.add(value)
            unique.append(value)
        counts[value] = counts.get(value, 0) + 1
        events.append(ScanEvent(visit, value, repeated, tuple(unique)))
    return events, [(value, counts[value]) for value in sorted(counts)]


def main() -> None:
    values = [7, 3, 7, 9, 3]
    events, frequencies = trace(values)
    for event in events:
        status = "repeat" if event.repeated else "first"
        unique = ",".join(str(value) for value in event.unique)
        print(f"visit={event.visit} value={event.value} {status} unique=[{unique}]")
    print("frequencies=" + ", ".join(f"{value}:{count}" for value, count in frequencies))


if __name__ == "__main__":
    main()
