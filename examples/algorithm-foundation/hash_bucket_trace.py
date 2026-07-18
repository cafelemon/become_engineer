from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BucketEvent:
    key: int
    bucket: int
    chain_before: int
    collision: bool


def trace(keys: list[int], bucket_count: int) -> tuple[list[BucketEvent], list[list[int]]]:
    if bucket_count <= 0:
        raise ValueError("bucket_count must be positive")
    buckets: list[list[int]] = [[] for _ in range(bucket_count)]
    events: list[BucketEvent] = []
    for key in keys:
        if key < 0:
            raise ValueError("teaching hash only accepts non-negative keys")
        bucket = key % bucket_count
        chain_before = len(buckets[bucket])
        events.append(BucketEvent(key, bucket, chain_before, chain_before > 0))
        buckets[bucket].append(key)
    return events, buckets


def main() -> None:
    events, buckets = trace([1, 5, 9, 2], 4)
    print("key bucket chain_before collision")
    for event in events:
        collision = "yes" if event.collision else "no"
        print(f"{event.key:<3} {event.bucket:<6} {event.chain_before:<12} {collision}")
    print("buckets=" + " ".join(f"{index}:{chain}" for index, chain in enumerate(buckets)))


if __name__ == "__main__":
    main()
