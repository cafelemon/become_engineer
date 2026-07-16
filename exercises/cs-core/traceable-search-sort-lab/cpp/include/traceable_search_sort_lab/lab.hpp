#pragma once

#include <cstddef>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace traceable_search_sort_lab {

class SortedValues {
 public:
  explicit SortedValues(std::span<const int> values);
  [[nodiscard]] const std::vector<int>& values() const noexcept;

 private:
  std::vector<int> values_;
};

struct SearchTrace {
  std::optional<std::size_t> index;
  std::size_t comparisons;
};

struct BoundTrace {
  std::size_t index;
  std::size_t comparisons;
};

struct RangeTrace {
  std::size_t first;
  std::size_t last;
  std::size_t comparisons;
};

[[nodiscard]] SearchTrace linear_search(const SortedValues& values, int target);
[[nodiscard]] BoundTrace lower_bound(const SortedValues& values, int target);
[[nodiscard]] BoundTrace upper_bound(const SortedValues& values, int target);
[[nodiscard]] RangeTrace equal_range(const SortedValues& values, int target);

struct TaggedValue {
  int key;
  std::string tag;

  bool operator==(const TaggedValue&) const = default;
};

struct InsertionSortTrace {
  std::vector<TaggedValue> items;
  std::size_t comparisons;
  std::size_t shifts;
};

struct SelectionSortTrace {
  std::vector<TaggedValue> items;
  std::size_t comparisons;
  std::size_t swaps;
};

struct MergeTrace {
  std::vector<TaggedValue> items;
  std::size_t comparisons;
  std::size_t writes;
};

struct MergePass {
  std::size_t width;
  std::vector<TaggedValue> items;
};

struct MergeSortTrace {
  std::vector<TaggedValue> items;
  std::size_t comparisons;
  std::size_t writes;
  std::vector<MergePass> passes;
};

[[nodiscard]] InsertionSortTrace insertion_sort(std::span<const TaggedValue> values,
                                                 bool descending = false);
[[nodiscard]] SelectionSortTrace selection_sort(std::span<const TaggedValue> values,
                                                 bool descending = false);
[[nodiscard]] bool preserves_equal_order(std::span<const TaggedValue> original,
                                         std::span<const TaggedValue> result);
[[nodiscard]] MergeTrace merge_sorted(std::span<const TaggedValue> left,
                                      std::span<const TaggedValue> right,
                                      bool descending = false);
[[nodiscard]] MergeSortTrace bottom_up_merge_sort(std::span<const TaggedValue> values,
                                                   bool descending = false);

[[nodiscard]] std::string build_search_report();
[[nodiscard]] std::string build_elementary_report();
[[nodiscard]] std::string build_merge_report();

}  // namespace traceable_search_sort_lab
