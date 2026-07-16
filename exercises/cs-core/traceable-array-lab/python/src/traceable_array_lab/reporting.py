from __future__ import annotations

from collections.abc import Sequence

from traceable_array_lab.lab import (
    analyze_utf8,
    build_growth_rows,
    checked_at,
    checked_grid_at,
    linear_search,
    simulate_growth,
    sum_grid_row,
    summarize_growth,
)


SAMPLE_VALUES = (7, 3, 9, 3)
DEFAULT_SIZES = (4, 8, 16, 32)


def _join_values(values: Sequence[int]) -> str:
    return ", ".join(str(value) for value in values)


def build_report() -> str:
    search = linear_search(SAMPLE_VALUES, 3)
    search_index = "未找到" if search.index is None else str(search.index)
    lines = [
        "可追踪数组实验",
        f"数据：{_join_values(SAMPLE_VALUES)}",
        f"index=2：{checked_at(SAMPLE_VALUES, 2)}",
        f"target=3：index={search_index}，comparisons={search.comparisons}",
        "",
        "增长表",
        "n | 常量访问 | 线性扫描 | 两两比较",
    ]
    for row in build_growth_rows(DEFAULT_SIZES):
        lines.append(
            f"{row.size} | {row.constant_steps} | {row.linear_steps} | {row.pair_steps}"
        )
    return "\n".join(lines)


def build_text_report() -> str:
    data = "A工🧪".encode("utf-8")
    trace = analyze_utf8(data)
    return "\n".join(
        [
            "UTF-8 扫描",
            "text：A工🧪",
            f"bytes={trace.byte_count}，code_points={trace.code_point_count}",
            f"ascii={trace.ascii_count}，multibyte={trace.multibyte_count}",
        ]
    )


def build_grid_report() -> str:
    values = (1, 2, 3, 4, 5, 6)
    cell = checked_grid_at(values, 2, 3, 1, 2)
    row = sum_grid_row(values, 2, 3, 0)
    return "\n".join(
        [
            "二维网格",
            "shape=2x3",
            "data：1, 2, 3 / 4, 5, 6",
            f"row=1，col=2：value={cell.value}，flat_index={cell.flat_index}",
            f"row=0：sum={row.total}，visits={row.visits}",
        ]
    )


def build_capacity_report() -> str:
    events = simulate_growth((7, 3, 9, 3, 5))
    summary = summarize_growth(events)
    lines = [
        "动态数组扩容",
        "append | size | capacity | copies | steps",
    ]
    for event in events:
        lines.append(
            f"{event.value} | {event.size} | {event.capacity} | "
            f"{event.copies} | {event.steps}"
        )
    lines.append(f"total_steps={summary.total_steps}")
    return "\n".join(lines)
