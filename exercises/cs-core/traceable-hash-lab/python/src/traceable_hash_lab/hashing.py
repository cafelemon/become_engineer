from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class BucketEvent:
    key: int
    bucket: int
    chain_before: int
    collision: bool


@dataclass(frozen=True)
class PutTrace:
    key: int
    bucket: int
    comparisons: int
    inserted: bool
    rehashed_from: int | None = None
    moved: int = 0


@dataclass(frozen=True)
class LookupTrace:
    value: int | None
    bucket: int
    comparisons: int


@dataclass(frozen=True)
class EraseTrace:
    removed: bool
    bucket: int
    comparisons: int


@dataclass(frozen=True)
class DuplicateTrace:
    value: int | None
    visits: int


@dataclass(frozen=True)
class FrequencyRow:
    value: int
    count: int


MAX_LOAD_FACTOR: Final[float] = 1.0


def bucket_index(key: int, bucket_count: int) -> int:
    if bucket_count <= 0:
        raise ValueError("bucket_count must be positive")
    if key < 0:
        raise ValueError("teaching hash only accepts non-negative keys")
    return key % bucket_count


def trace_bucket_inserts(keys: list[int], bucket_count: int) -> list[BucketEvent]:
    chains = build_bucket_chains([], bucket_count)
    events: list[BucketEvent] = []
    for key in keys:
        bucket = bucket_index(key, bucket_count)
        chain_before = len(chains[bucket])
        events.append(BucketEvent(key, bucket, chain_before, chain_before > 0))
        chains[bucket].append(key)
    return events


def build_bucket_chains(keys: list[int], bucket_count: int) -> list[list[int]]:
    if bucket_count <= 0:
        raise ValueError("bucket_count must be positive")
    chains: list[list[int]] = [[] for _ in range(bucket_count)]
    for key in keys:
        chains[bucket_index(key, bucket_count)].append(key)
    return chains


def first_collision(keys: list[int], bucket_count: int) -> BucketEvent | None:
    return next((event for event in trace_bucket_inserts(keys, bucket_count) if event.collision), None)


class TraceableHashMap:
    def __init__(self, bucket_count: int = 4) -> None:
        if bucket_count <= 0:
            raise ValueError("bucket_count must be positive")
        self._buckets: list[list[tuple[int, int]]] = [[] for _ in range(bucket_count)]
        self._size = 0

    def put(self, key: int, value: int) -> PutTrace:
        bucket = bucket_index(key, self.bucket_count())
        chain = self._buckets[bucket]
        comparisons = 0
        for index, (stored_key, _) in enumerate(chain):
            comparisons += 1
            if stored_key == key:
                chain[index] = (key, value)
                return PutTrace(key, bucket, comparisons, False)

        rehashed_from: int | None = None
        moved = 0
        if self._size + 1 > self.bucket_count() * MAX_LOAD_FACTOR:
            rehashed_from = self.bucket_count()
            moved = self._size
            self._rehash(rehashed_from * 2)
            bucket = bucket_index(key, self.bucket_count())
            chain = self._buckets[bucket]
            comparisons = 0
            for stored_key, _ in chain:
                comparisons += 1
                if stored_key == key:
                    raise AssertionError("new key unexpectedly appeared during rehash")

        chain.append((key, value))
        self._size += 1
        return PutTrace(key, bucket, comparisons, True, rehashed_from, moved)

    def get(self, key: int) -> LookupTrace:
        bucket = bucket_index(key, self.bucket_count())
        comparisons = 0
        for stored_key, value in self._buckets[bucket]:
            comparisons += 1
            if stored_key == key:
                return LookupTrace(value, bucket, comparisons)
        return LookupTrace(None, bucket, comparisons)

    def erase(self, key: int) -> EraseTrace:
        bucket = bucket_index(key, self.bucket_count())
        chain = self._buckets[bucket]
        comparisons = 0
        for index, (stored_key, _) in enumerate(chain):
            comparisons += 1
            if stored_key == key:
                del chain[index]
                self._size -= 1
                return EraseTrace(True, bucket, comparisons)
        return EraseTrace(False, bucket, comparisons)

    def size(self) -> int:
        return self._size

    def bucket_count(self) -> int:
        return len(self._buckets)

    def load_factor(self) -> float:
        return self._size / self.bucket_count()

    def items_sorted(self) -> list[tuple[int, int]]:
        return sorted(item for chain in self._buckets for item in chain)

    def _rehash(self, new_bucket_count: int) -> None:
        old_items = [item for chain in self._buckets for item in chain]
        self._buckets = [[] for _ in range(new_bucket_count)]
        for key, value in old_items:
            self._buckets[bucket_index(key, new_bucket_count)].append((key, value))


def first_duplicate(values: list[int]) -> DuplicateTrace:
    seen: set[int] = set()
    for visits, value in enumerate(values, start=1):
        if value in seen:
            return DuplicateTrace(value, visits)
        seen.add(value)
    return DuplicateTrace(None, len(values))


def count_frequencies(values: list[int]) -> list[FrequencyRow]:
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [FrequencyRow(value, counts[value]) for value in sorted(counts)]


def deduplicate_preserving_order(values: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
