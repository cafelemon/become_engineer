from __future__ import annotations

from collections.abc import Sequence

from traceable_array_lab.lab import build_growth_rows, checked_at, linear_search


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
