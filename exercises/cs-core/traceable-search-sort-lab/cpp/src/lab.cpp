#include "traceable_search_sort_lab/lab.hpp"

#include <algorithm>
#include <sstream>
#include <stdexcept>
#include <unordered_map>
#include <utility>

namespace traceable_search_sort_lab {
namespace {

bool comes_before(const TaggedValue& left, const TaggedValue& right, bool descending) {
  return descending ? left.key > right.key : left.key < right.key;
}

std::string format_items(std::span<const TaggedValue> items) {
  std::ostringstream output;
  for (std::size_t index = 0; index < items.size(); ++index) {
    if (index != 0) {
      output << ", ";
    }
    output << items[index].key << items[index].tag;
  }
  return output.str();
}

}  // namespace

SortedValues::SortedValues(std::span<const int> values) : values_(values.begin(), values.end()) {
  if (!std::is_sorted(values_.begin(), values_.end())) {
    throw std::invalid_argument("values must be sorted in nondecreasing order");
  }
}

const std::vector<int>& SortedValues::values() const noexcept { return values_; }

SearchTrace linear_search(const SortedValues& values, int target) {
  std::size_t comparisons = 0;
  for (std::size_t index = 0; index < values.values().size(); ++index) {
    ++comparisons;
    if (values.values()[index] == target) {
      return {index, comparisons};
    }
  }
  return {std::nullopt, comparisons};
}

BoundTrace lower_bound(const SortedValues& values, int target) {
  std::size_t left = 0;
  std::size_t right = values.values().size();
  std::size_t comparisons = 0;
  while (left < right) {
    const std::size_t middle = left + (right - left) / 2;
    ++comparisons;
    if (values.values()[middle] < target) {
      left = middle + 1;
    } else {
      right = middle;
    }
  }
  return {left, comparisons};
}

BoundTrace upper_bound(const SortedValues& values, int target) {
  std::size_t left = 0;
  std::size_t right = values.values().size();
  std::size_t comparisons = 0;
  while (left < right) {
    const std::size_t middle = left + (right - left) / 2;
    ++comparisons;
    if (values.values()[middle] <= target) {
      left = middle + 1;
    } else {
      right = middle;
    }
  }
  return {left, comparisons};
}

RangeTrace equal_range(const SortedValues& values, int target) {
  const BoundTrace lower = lower_bound(values, target);
  const BoundTrace upper = upper_bound(values, target);
  return {lower.index, upper.index, lower.comparisons + upper.comparisons};
}

InsertionSortTrace insertion_sort(std::span<const TaggedValue> values, bool descending) {
  std::vector<TaggedValue> items(values.begin(), values.end());
  std::size_t comparisons = 0;
  std::size_t shifts = 0;
  for (std::size_t current_index = 1; current_index < items.size(); ++current_index) {
    TaggedValue current = items[current_index];
    std::size_t position = current_index;
    while (position > 0) {
      ++comparisons;
      if (!comes_before(current, items[position - 1], descending)) {
        break;
      }
      items[position] = items[position - 1];
      ++shifts;
      --position;
    }
    items[position] = std::move(current);
  }
  return {std::move(items), comparisons, shifts};
}

SelectionSortTrace selection_sort(std::span<const TaggedValue> values, bool descending) {
  std::vector<TaggedValue> items(values.begin(), values.end());
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  for (std::size_t start = 0; start < items.size(); ++start) {
    std::size_t selected = start;
    for (std::size_t candidate = start + 1; candidate < items.size(); ++candidate) {
      ++comparisons;
      if (comes_before(items[candidate], items[selected], descending)) {
        selected = candidate;
      }
    }
    if (selected != start) {
      std::swap(items[start], items[selected]);
      ++swaps;
    }
  }
  return {std::move(items), comparisons, swaps};
}

bool preserves_equal_order(std::span<const TaggedValue> original,
                           std::span<const TaggedValue> result) {
  std::unordered_map<int, std::vector<std::string>> original_tags;
  std::unordered_map<int, std::vector<std::string>> result_tags;
  for (const TaggedValue& item : original) {
    original_tags[item.key].push_back(item.tag);
  }
  for (const TaggedValue& item : result) {
    result_tags[item.key].push_back(item.tag);
  }
  return original_tags == result_tags;
}

MergeTrace merge_sorted(std::span<const TaggedValue> left,
                        std::span<const TaggedValue> right,
                        bool descending) {
  std::vector<TaggedValue> merged;
  merged.reserve(left.size() + right.size());
  std::size_t left_index = 0;
  std::size_t right_index = 0;
  std::size_t comparisons = 0;
  while (left_index < left.size() && right_index < right.size()) {
    ++comparisons;
    if (comes_before(right[right_index], left[left_index], descending)) {
      merged.push_back(right[right_index]);
      ++right_index;
    } else {
      merged.push_back(left[left_index]);
      ++left_index;
    }
  }
  merged.insert(merged.end(), left.begin() + static_cast<std::ptrdiff_t>(left_index), left.end());
  merged.insert(merged.end(), right.begin() + static_cast<std::ptrdiff_t>(right_index), right.end());
  const std::size_t writes = merged.size();
  return {std::move(merged), comparisons, writes};
}

MergeSortTrace bottom_up_merge_sort(std::span<const TaggedValue> values, bool descending) {
  std::vector<TaggedValue> items(values.begin(), values.end());
  std::vector<MergePass> passes;
  std::size_t comparisons = 0;
  std::size_t writes = 0;
  for (std::size_t width = 1; width < items.size(); width *= 2) {
    std::vector<TaggedValue> next_items;
    next_items.reserve(items.size());
    for (std::size_t start = 0; start < items.size(); start += width * 2) {
      const std::size_t middle = std::min(start + width, items.size());
      const std::size_t end = std::min(start + width * 2, items.size());
      const auto left = std::span<const TaggedValue>(items).subspan(start, middle - start);
      const auto right = std::span<const TaggedValue>(items).subspan(middle, end - middle);
      MergeTrace merged = merge_sorted(left, right, descending);
      comparisons += merged.comparisons;
      writes += merged.writes;
      next_items.insert(next_items.end(), merged.items.begin(), merged.items.end());
    }
    items = std::move(next_items);
    passes.push_back({width, items});
  }
  return {std::move(items), comparisons, writes, std::move(passes)};
}

std::string build_search_report() {
  const std::vector<int> source{1, 3, 3, 3, 7, 9};
  const SortedValues values(source);
  constexpr int target = 3;
  const SearchTrace linear = linear_search(values, target);
  const BoundTrace lower = lower_bound(values, target);
  const BoundTrace upper = upper_bound(values, target);
  const RangeTrace range = equal_range(values, target);
  std::ostringstream output;
  output << "有序查找实验\n"
         << "data：1, 3, 3, 3, 7, 9\n"
         << "target=3\n"
         << "linear：index=" << *linear.index << "，comparisons=" << linear.comparisons << '\n'
         << "lower_bound：index=" << lower.index << "，comparisons=" << lower.comparisons << '\n'
         << "upper_bound：index=" << upper.index << "，comparisons=" << upper.comparisons << '\n'
         << "equal_range：[" << range.first << ", " << range.last << ')';
  return output.str();
}

std::string build_elementary_report() {
  const std::vector<TaggedValue> values{{3, "A"}, {1, "B"}, {3, "C"}, {2, "D"}};
  const InsertionSortTrace insertion = insertion_sort(values);
  const SelectionSortTrace selection = selection_sort(values);
  std::ostringstream output;
  output << "基础比较排序\n"
         << "data：" << format_items(values) << '\n'
         << "insertion：" << format_items(insertion.items) << '\n'
         << "comparisons=" << insertion.comparisons << "，shifts=" << insertion.shifts
         << "，stable=" << (preserves_equal_order(values, insertion.items) ? "yes" : "no") << '\n'
         << "selection：" << format_items(selection.items) << '\n'
         << "comparisons=" << selection.comparisons << "，swaps=" << selection.swaps
         << "，stable=" << (preserves_equal_order(values, selection.items) ? "yes" : "no");
  return output.str();
}

std::string build_merge_report() {
  const std::vector<TaggedValue> values{{3, "A"}, {1, "B"}, {3, "C"}, {2, "D"}};
  const MergeSortTrace trace = bottom_up_merge_sort(values);
  std::ostringstream output;
  output << "迭代归并排序\n" << "data：" << format_items(values) << '\n';
  for (const MergePass& pass : trace.passes) {
    output << "width=" << pass.width << "：";
    const std::size_t group_size = pass.width * 2;
    for (std::size_t start = 0; start < pass.items.size(); start += group_size) {
      if (start != 0) {
        output << " | ";
      }
      const std::size_t count = std::min(group_size, pass.items.size() - start);
      output << format_items(std::span<const TaggedValue>(pass.items).subspan(start, count));
    }
    output << '\n';
  }
  output << "comparisons=" << trace.comparisons << "，writes=" << trace.writes
         << "，passes=" << trace.passes.size() << '\n'
         << "stable=" << (preserves_equal_order(values, trace.items) ? "yes" : "no")
         << "，input_unchanged=yes";
  return output.str();
}

}  // namespace traceable_search_sort_lab
