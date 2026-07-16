#include "traceable_array_lab/lab.hpp"

#include <array>
#include <stdexcept>
#include <string>
#include <vector>

using traceable_array_lab::AdjacentTrace;
using traceable_array_lab::GrowthRow;
using traceable_array_lab::SearchTrace;

namespace {

void expect(bool condition, const char* message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

template <typename Function>
void expect_out_of_range(Function function) {
    bool raised = false;
    try {
        function();
    } catch (const std::out_of_range&) {
        raised = true;
    }
    expect(raised, "expected std::out_of_range");
}

}  // namespace

int main() {
    const std::vector values{7, 3, 9, 3};
    expect(traceable_array_lab::checked_at(values, 0) == 7, "first element");
    expect(traceable_array_lab::checked_at(values, 3) == 3, "last element");
    expect_out_of_range([&values] { traceable_array_lab::checked_at(values, -1); });
    expect_out_of_range([&values] { traceable_array_lab::checked_at(values, 4); });
    const std::vector<int> empty;
    expect_out_of_range([&empty] { traceable_array_lab::checked_at(empty, 0); });

    const auto changed = traceable_array_lab::replace_at_copy(values, 1, 8);
    expect(changed == std::vector{7, 8, 9, 3}, "replacement copy");
    expect(values == std::vector{7, 3, 9, 3}, "original remains unchanged");

    expect(traceable_array_lab::linear_search(values, 3) == SearchTrace{1, 2}, "found search trace");
    expect(traceable_array_lab::linear_search(values, 4) == SearchTrace{std::nullopt, 4}, "missing search trace");
    expect(traceable_array_lab::linear_search(empty, 4) == SearchTrace{std::nullopt, 0}, "empty search trace");

    constexpr std::array<std::size_t, 3> sizes{0, 4, 8};
    const auto rows = traceable_array_lab::build_growth_rows(sizes);
    expect(rows == std::vector{
        GrowthRow{0, 0, 0, 0},
        GrowthRow{4, 1, 4, 6},
        GrowthRow{8, 1, 8, 28},
    }, "growth rows");

    expect(traceable_array_lab::count_adjacent_increases(empty) == AdjacentTrace{0, 0}, "empty adjacent trace");
    const std::array one{4};
    expect(traceable_array_lab::count_adjacent_increases(one) == AdjacentTrace{0, 0}, "single adjacent trace");
    const std::array rising{1, 2, 3};
    expect(traceable_array_lab::count_adjacent_increases(rising) == AdjacentTrace{2, 2}, "rising adjacent trace");
    const std::array repeated{1, 1, 2};
    expect(traceable_array_lab::count_adjacent_increases(repeated) == AdjacentTrace{1, 2}, "repeated adjacent trace");

    const std::string expected =
        "可追踪数组实验\n"
        "数据：7, 3, 9, 3\n"
        "index=2：9\n"
        "target=3：index=1，comparisons=2\n\n"
        "增长表\n"
        "n | 常量访问 | 线性扫描 | 两两比较\n"
        "4 | 1 | 4 | 6\n"
        "8 | 1 | 8 | 28\n"
        "16 | 1 | 16 | 120\n"
        "32 | 1 | 32 | 496";
    expect(traceable_array_lab::build_report() == expected, "report contract");
    return 0;
}
