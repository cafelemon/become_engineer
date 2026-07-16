from traceable_hash_lab.hashing import (
    TraceableHashMap,
    build_bucket_chains,
    count_frequencies,
    deduplicate_preserving_order,
    first_duplicate,
    trace_bucket_inserts,
)


def _join(values: list[int]) -> str:
    return ", ".join(str(value) for value in values)


def build_hash_report() -> str:
    keys = [1, 5, 9, 2]
    bucket_count = 4
    rows = ["可追踪哈希实验", f"bucket_count={bucket_count}", "key | bucket | chain_before | collision"]
    rows.extend(
        f"{event.key} | {event.bucket} | {event.chain_before} | {'yes' if event.collision else 'no'}"
        for event in trace_bucket_inserts(keys, bucket_count)
    )
    buckets = build_bucket_chains(keys, bucket_count)
    rows.append("buckets：" + " ".join(f"{index}=[{_join(chain)}]" for index, chain in enumerate(buckets)))
    return "\n".join(rows)


def build_table_report() -> str:
    table = TraceableHashMap()
    rows = ["分离链接哈希表"]
    for key, value in [(1, 10), (5, 50), (9, 90), (2, 20), (13, 130)]:
        trace = table.put(key, value)
        row = (
            f"put {key}={value}：inserted={'yes' if trace.inserted else 'no'}，"
            f"bucket={trace.bucket}，comparisons={trace.comparisons}"
        )
        if trace.rehashed_from is not None:
            row += f"，rehash={trace.rehashed_from}->{table.bucket_count()}，moved={trace.moved}"
        rows.append(row)
    lookup = table.get(9)
    rows.append(f"get 9：value={lookup.value}，bucket={lookup.bucket}，comparisons={lookup.comparisons}")
    rows.append(f"size={table.size()}，buckets={table.bucket_count()}，load_factor={table.load_factor():.3f}")
    return "\n".join(rows)


def build_applications_report() -> str:
    values = [7, 3, 7, 9, 3]
    duplicate = first_duplicate(values)
    frequencies = count_frequencies(values)
    return "\n".join(
        [
            "集合与频次映射",
            f"data：{_join(values)}",
            f"first_duplicate={duplicate.value}，visits={duplicate.visits}",
            f"unique_in_order：{_join(deduplicate_preserving_order(values))}",
            "frequencies：" + ", ".join(f"{row.value}={row.count}" for row in frequencies),
        ]
    )
