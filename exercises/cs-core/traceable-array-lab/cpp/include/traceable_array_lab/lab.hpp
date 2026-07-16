#pragma once

#include <cstddef>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace traceable_array_lab {

struct SearchTrace {
    std::optional<std::size_t> index;
    std::size_t comparisons;

    bool operator==(const SearchTrace&) const = default;
};

struct GrowthRow {
    std::size_t size;
    std::size_t constant_steps;
    std::size_t linear_steps;
    std::size_t pair_steps;

    bool operator==(const GrowthRow&) const = default;
};

struct AdjacentTrace {
    std::size_t increases;
    std::size_t comparisons;

    bool operator==(const AdjacentTrace&) const = default;
};

struct Utf8Trace {
    std::size_t byte_count;
    std::size_t code_point_count;
    std::size_t ascii_count;
    std::size_t multibyte_count;

    bool operator==(const Utf8Trace&) const = default;
};

struct GridCell {
    int value;
    std::size_t flat_index;

    bool operator==(const GridCell&) const = default;
};

struct RowTrace {
    int total;
    std::size_t visits;

    bool operator==(const RowTrace&) const = default;
};

struct CapacityEvent {
    int value;
    std::size_t size;
    std::size_t capacity;
    std::size_t copies;
    std::size_t steps;

    bool operator==(const CapacityEvent&) const = default;
};

struct GrowthSummary {
    std::size_t total_appends;
    std::size_t total_copies;
    std::size_t total_steps;
    std::size_t final_capacity;

    bool operator==(const GrowthSummary&) const = default;
};

int checked_at(std::span<const int> values, std::ptrdiff_t index);
std::vector<int> replace_at_copy(
    std::span<const int> values,
    std::ptrdiff_t index,
    int value
);
SearchTrace linear_search(std::span<const int> values, int target);
std::vector<GrowthRow> build_growth_rows(std::span<const std::size_t> sizes);
AdjacentTrace count_adjacent_increases(std::span<const int> values);
Utf8Trace analyze_utf8(std::string_view data);
GridCell checked_grid_at(
    std::span<const int> values,
    std::size_t rows,
    std::size_t columns,
    std::ptrdiff_t row,
    std::ptrdiff_t column
);
RowTrace sum_grid_row(
    std::span<const int> values,
    std::size_t rows,
    std::size_t columns,
    std::ptrdiff_t row
);
std::vector<CapacityEvent> simulate_growth(
    std::span<const int> values,
    std::size_t initial_capacity = 0
);
GrowthSummary summarize_growth(std::span<const CapacityEvent> events);
std::string build_report();
std::string build_text_report();
std::string build_grid_report();
std::string build_capacity_report();

}  // namespace traceable_array_lab
