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

int checked_at(std::span<const int> values, std::ptrdiff_t index);
std::vector<int> replace_at_copy(
    std::span<const int> values,
    std::ptrdiff_t index,
    int value
);
SearchTrace linear_search(std::span<const int> values, int target);
std::vector<GrowthRow> build_growth_rows(std::span<const std::size_t> sizes);
AdjacentTrace count_adjacent_increases(std::span<const int> values);
std::string build_report();

}  // namespace traceable_array_lab
