from __future__ import annotations

from dataclasses import dataclass
from threading import Barrier, Lock, Thread


@dataclass(frozen=True)
class CounterResult:
    expected: int
    actual: int


def lost_update_demo() -> CounterResult:
    counter = {"value": 0}
    both_have_read = Barrier(2)

    def increment_once() -> None:
        snapshot = counter["value"]
        both_have_read.wait()
        counter["value"] = snapshot + 1

    threads = [Thread(target=increment_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return CounterResult(expected=2, actual=counter["value"])


def locked_counter(workers: int = 2, increments: int = 1_000) -> CounterResult:
    counter = {"value": 0}
    lock = Lock()

    def increment_many() -> None:
        for _ in range(increments):
            with lock:
                counter["value"] += 1

    threads = [Thread(target=increment_many) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return CounterResult(expected=workers * increments, actual=counter["value"])


def main() -> None:
    race = lost_update_demo()
    protected = locked_counter()
    print(f"without lock: expected={race.expected} actual={race.actual}")
    print(f"with lock: expected={protected.expected} actual={protected.actual}")


if __name__ == "__main__":
    main()
