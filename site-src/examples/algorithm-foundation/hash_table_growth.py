from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PutEvent:
    key: int
    bucket: int
    comparisons: int
    inserted: bool
    rehashed_from: int | None
    moved: int


class HashTable:
    def __init__(self, bucket_count: int = 4) -> None:
        self._buckets: list[list[tuple[int, int]]] = [[] for _ in range(bucket_count)]
        self._size = 0

    def put(self, key: int, value: int) -> PutEvent:
        bucket = key % len(self._buckets)
        comparisons = 0
        for index, (stored_key, _) in enumerate(self._buckets[bucket]):
            comparisons += 1
            if stored_key == key:
                self._buckets[bucket][index] = (key, value)
                return PutEvent(key, bucket, comparisons, False, None, 0)

        rehashed_from: int | None = None
        moved = 0
        if self._size + 1 > len(self._buckets):
            rehashed_from = len(self._buckets)
            moved = self._size
            old_items = [item for chain in self._buckets for item in chain]
            self._buckets = [[] for _ in range(rehashed_from * 2)]
            for old_key, old_value in old_items:
                self._buckets[old_key % len(self._buckets)].append((old_key, old_value))
            bucket = key % len(self._buckets)
            comparisons = sum(stored_key != key for stored_key, _ in self._buckets[bucket])

        self._buckets[bucket].append((key, value))
        self._size += 1
        return PutEvent(key, bucket, comparisons, True, rehashed_from, moved)

    def summary(self) -> str:
        return f"size={self._size} buckets={len(self._buckets)} load={self._size / len(self._buckets):.3f}"


def main() -> None:
    table = HashTable()
    for key in (1, 5, 9, 2, 13):
        event = table.put(key, key * 10)
        growth = "-" if event.rehashed_from is None else f"{event.rehashed_from}->8 moved={event.moved}"
        print(f"put {key:<2} bucket={event.bucket} comparisons={event.comparisons} rehash={growth}")
    print(table.summary())


if __name__ == "__main__":
    main()
