#include "traceable_array_lab/lab.hpp"

#include <array>
#include <sstream>
#include <stdexcept>

namespace traceable_array_lab {
namespace {

std::size_t checked_index(std::span<const int> values, std::ptrdiff_t index) {
    if (index < 0 || static_cast<std::size_t>(index) >= values.size()) {
        throw std::out_of_range("array index outside sequence boundary");
    }
    return static_cast<std::size_t>(index);
}

}  // namespace

int checked_at(std::span<const int> values, std::ptrdiff_t index) {
    return values[checked_index(values, index)];
}

std::vector<int> replace_at_copy(
    std::span<const int> values,
    std::ptrdiff_t index,
    int value
) {
    const auto valid_index = checked_index(values, index);
    std::vector<int> copied(values.begin(), values.end());
    copied.at(valid_index) = value;
    return copied;
}

SearchTrace linear_search(std::span<const int> values, int target) {
    std::size_t comparisons = 0;
    for (std::size_t index = 0; index < values.size(); ++index) {
        ++comparisons;
        if (values[index] == target) {
            return SearchTrace{index, comparisons};
        }
    }
    return SearchTrace{std::nullopt, comparisons};
}

std::vector<GrowthRow> build_growth_rows(std::span<const std::size_t> sizes) {
    std::vector<GrowthRow> rows;
    rows.reserve(sizes.size());
    for (const auto size : sizes) {
        rows.push_back(GrowthRow{
            size,
            size > 0 ? 1U : 0U,
            size,
            size * (size - (size > 0 ? 1U : 0U)) / 2U,
        });
    }
    return rows;
}

AdjacentTrace count_adjacent_increases(std::span<const int> values) {
    std::size_t increases = 0;
    std::size_t comparisons = 0;
    for (std::size_t index = 1; index < values.size(); ++index) {
        ++comparisons;
        if (values[index] > values[index - 1]) {
            ++increases;
        }
    }
    return AdjacentTrace{increases, comparisons};
}

std::string build_report() {
    constexpr std::array values{7, 3, 9, 3};
    constexpr std::array<std::size_t, 4> sizes{4, 8, 16, 32};
    const auto search = linear_search(values, 3);

    std::ostringstream output;
    output << "可追踪数组实验\n"
           << "数据：7, 3, 9, 3\n"
           << "index=2：" << checked_at(values, 2) << '\n'
           << "target=3：index=" << search.index.value()
           << "，comparisons=" << search.comparisons << "\n\n"
           << "增长表\n"
           << "n | 常量访问 | 线性扫描 | 两两比较\n";
    const auto rows = build_growth_rows(sizes);
    for (std::size_t index = 0; index < rows.size(); ++index) {
        const auto& row = rows[index];
        output << row.size << " | " << row.constant_steps << " | "
               << row.linear_steps << " | " << row.pair_steps;
        if (index + 1 < rows.size()) {
            output << '\n';
        }
    }
    return output.str();
}

}  // namespace traceable_array_lab
