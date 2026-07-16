from traceable_search_sort_lab.searching import (
    SortedValues,
    equal_range,
    linear_search,
    lower_bound,
    upper_bound,
)
from traceable_search_sort_lab.sorting import (
    TaggedValue,
    bottom_up_merge_sort,
    insertion_sort,
    preserves_equal_order,
    selection_sort,
)


def _format_items(items: tuple[TaggedValue, ...]) -> str:
    return ", ".join(f"{item.key}{item.tag}" for item in items)


def build_search_report() -> str:
    values = SortedValues.from_values([1, 3, 3, 3, 7, 9])
    target = 3
    linear = linear_search(values, target)
    lower = lower_bound(values, target)
    upper = upper_bound(values, target)
    match_range = equal_range(values, target)
    return "\n".join(
        [
            "有序查找实验",
            "data：1, 3, 3, 3, 7, 9",
            "target=3",
            f"linear：index={linear.index}，comparisons={linear.comparisons}",
            f"lower_bound：index={lower.index}，comparisons={lower.comparisons}",
            f"upper_bound：index={upper.index}，comparisons={upper.comparisons}",
            f"equal_range：[{match_range.first}, {match_range.last})",
        ]
    )


def build_elementary_report() -> str:
    values = (TaggedValue(3, "A"), TaggedValue(1, "B"), TaggedValue(3, "C"), TaggedValue(2, "D"))
    insertion = insertion_sort(values)
    selection = selection_sort(values)
    return "\n".join(
        [
            "基础比较排序",
            f"data：{_format_items(values)}",
            f"insertion：{_format_items(insertion.items)}",
            f"comparisons={insertion.comparisons}，shifts={insertion.shifts}，stable={'yes' if preserves_equal_order(values, insertion.items) else 'no'}",
            f"selection：{_format_items(selection.items)}",
            f"comparisons={selection.comparisons}，swaps={selection.swaps}，stable={'yes' if preserves_equal_order(values, selection.items) else 'no'}",
        ]
    )


def build_merge_report() -> str:
    values = (TaggedValue(3, "A"), TaggedValue(1, "B"), TaggedValue(3, "C"), TaggedValue(2, "D"))
    trace = bottom_up_merge_sort(values)
    pass_lines: list[str] = []
    for merge_pass in trace.passes:
        group_size = merge_pass.width * 2
        groups = [
            _format_items(merge_pass.items[start : start + group_size])
            for start in range(0, len(merge_pass.items), group_size)
        ]
        pass_lines.append(f"width={merge_pass.width}：{' | '.join(groups)}")
    return "\n".join(
        [
            "迭代归并排序",
            f"data：{_format_items(values)}",
            *pass_lines,
            f"comparisons={trace.comparisons}，writes={trace.writes}，passes={len(trace.passes)}",
            f"stable={'yes' if preserves_equal_order(values, trace.items) else 'no'}，input_unchanged=yes",
        ]
    )
