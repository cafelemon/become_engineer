#include "traceable_search_sort_lab/lab.hpp"

#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <stdexcept>
#include <string>
#include <vector>

using namespace traceable_search_sort_lab;

namespace {

std::vector<std::string> tags(const std::vector<TaggedValue>& values) {
  std::vector<std::string> result;
  for (const TaggedValue& value : values) {
    result.push_back(value.tag);
  }
  return result;
}

void test_searching() {
  std::vector<int> source{1, 3, 3, 3, 7, 9};
  const SortedValues values(source);
  source[0] = 99;
  assert(values.values().front() == 1);
  const SearchTrace linear = linear_search(values, 3);
  assert(linear.index == 1);
  assert(linear.comparisons == 2);
  assert(lower_bound(values, 3).index == 1);
  assert(lower_bound(values, 3).comparisons == 3);
  assert(upper_bound(values, 3).index == 4);
  assert(upper_bound(values, 3).comparisons == 3);
  const RangeTrace range = equal_range(values, 3);
  assert(range.first == 1 && range.last == 4 && range.comparisons == 6);
  assert(lower_bound(values, 10).index == values.values().size());
  assert(!linear_search(values, 8).index.has_value());
  assert(linear_search(values, 8).comparisons == values.values().size());

  const SortedValues empty(std::vector<int>{});
  assert(lower_bound(empty, 1).index == 0);
  assert(linear_search(empty, 1).comparisons == 0);
  bool rejected = false;
  try {
    const SortedValues invalid(std::vector<int>{1, 4, 2});
    static_cast<void>(invalid);
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  assert(rejected);
}

void test_elementary_sorting() {
  const std::vector<TaggedValue> values{{3, "A"}, {1, "B"}, {3, "C"}, {2, "D"}};
  const InsertionSortTrace insertion = insertion_sort(values);
  assert((tags(insertion.items) == std::vector<std::string>{"B", "D", "A", "C"}));
  assert(insertion.comparisons == 5 && insertion.shifts == 3);
  assert(preserves_equal_order(values, insertion.items));

  const SelectionSortTrace selection = selection_sort(values);
  assert((tags(selection.items) == std::vector<std::string>{"B", "D", "C", "A"}));
  assert(selection.comparisons == 6 && selection.swaps == 2);
  assert(!preserves_equal_order(values, selection.items));

  const InsertionSortTrace descending = insertion_sort(values, true);
  assert((tags(descending.items) == std::vector<std::string>{"A", "C", "D", "B"}));
  assert(preserves_equal_order(values, descending.items));
  assert(values.front().tag == "A");
  assert(insertion_sort(std::vector<TaggedValue>{}).items.empty());
}

void test_merge_sorting() {
  const std::vector<TaggedValue> left{{3, "L"}};
  const std::vector<TaggedValue> right{{3, "R"}};
  const MergeTrace merged = merge_sorted(left, right);
  assert((tags(merged.items) == std::vector<std::string>{"L", "R"}));
  assert(merged.comparisons == 1 && merged.writes == 2);
  assert(merge_sorted(std::vector<TaggedValue>{}, right).items == right);
  assert(merge_sorted(left, std::vector<TaggedValue>{}).items == left);

  const std::vector<TaggedValue> values{{3, "A"}, {1, "B"}, {3, "C"}, {2, "D"}};
  const MergeSortTrace trace = bottom_up_merge_sort(values);
  assert((tags(trace.items) == std::vector<std::string>{"B", "D", "A", "C"}));
  assert(trace.comparisons == 5 && trace.writes == 8);
  assert(trace.passes.size() == 2);
  assert(trace.passes[0].width == 1 && trace.passes[1].width == 2);
  assert(preserves_equal_order(values, trace.items));

  const std::vector<TaggedValue> odd{{2, "A"}, {1, "B"}, {2, "C"}};
  const MergeSortTrace descending = bottom_up_merge_sort(odd, true);
  assert((tags(descending.items) == std::vector<std::string>{"A", "C", "B"}));
  assert(preserves_equal_order(odd, descending.items));
  assert(odd.front().tag == "A");
}

void test_reports() {
  assert(build_search_report() ==
         "有序查找实验\n"
         "data：1, 3, 3, 3, 7, 9\n"
         "target=3\n"
         "linear：index=1，comparisons=2\n"
         "lower_bound：index=1，comparisons=3\n"
         "upper_bound：index=4，comparisons=3\n"
         "equal_range：[1, 4)");
  assert(build_elementary_report() ==
         "基础比较排序\n"
         "data：3A, 1B, 3C, 2D\n"
         "insertion：1B, 2D, 3A, 3C\n"
         "comparisons=5，shifts=3，stable=yes\n"
         "selection：1B, 2D, 3C, 3A\n"
         "comparisons=6，swaps=2，stable=no");
  assert(build_merge_report() ==
         "迭代归并排序\n"
         "data：3A, 1B, 3C, 2D\n"
         "width=1：1B, 3A | 2D, 3C\n"
         "width=2：1B, 2D, 3A, 3C\n"
         "comparisons=5，writes=8，passes=2\n"
         "stable=yes，input_unchanged=yes");
}

}  // namespace

int main() {
  test_searching();
  test_elementary_sorting();
  test_merge_sorting();
  test_reports();
  return 0;
}
