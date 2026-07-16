#include "traceable_array_lab/lab.hpp"

#include <array>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using traceable_array_lab::AdjacentTrace;
using traceable_array_lab::CapacityEvent;
using traceable_array_lab::GridCell;
using traceable_array_lab::GrowthRow;
using traceable_array_lab::GrowthSummary;
using traceable_array_lab::RowTrace;
using traceable_array_lab::SearchTrace;
using traceable_array_lab::Utf8Trace;

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

template <typename Function>
void expect_invalid_argument(Function function) {
    bool raised = false;
    try {
        function();
    } catch (const std::invalid_argument&) {
        raised = true;
    }
    expect(raised, "expected std::invalid_argument");
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

    const std::string utf8_sample = "A\xE5\xB7\xA5\xF0\x9F\xA7\xAA";
    expect(traceable_array_lab::analyze_utf8(utf8_sample) == Utf8Trace{8, 3, 1, 2}, "UTF-8 trace");
    expect(traceable_array_lab::analyze_utf8("") == Utf8Trace{0, 0, 0, 0}, "empty UTF-8 trace");
    for (const std::string& invalid : {
             std::string{"\x80"},
             std::string{"\xC2\x41"},
             std::string{"\xC0\xAF"},
             std::string{"\xED\xA0\x80"},
             std::string{"\xF4\x90\x80\x80"},
             std::string{"\xE5\xB7"},
         }) {
        expect_invalid_argument([&invalid] { traceable_array_lab::analyze_utf8(invalid); });
    }

    constexpr std::array grid{1, 2, 3, 4, 5, 6};
    expect(traceable_array_lab::checked_grid_at(grid, 2, 3, 0, 0) == GridCell{1, 0}, "first grid cell");
    expect(traceable_array_lab::checked_grid_at(grid, 2, 3, 1, 2) == GridCell{6, 5}, "last grid cell");
    expect(traceable_array_lab::sum_grid_row(grid, 2, 3, 0) == RowTrace{6, 3}, "grid row trace");
    expect_invalid_argument([&grid] { traceable_array_lab::checked_grid_at(grid, 2, 4, 0, 0); });
    expect_invalid_argument([&empty] {
        traceable_array_lab::checked_grid_at(
            empty,
            std::numeric_limits<std::size_t>::max(),
            2,
            0,
            0
        );
    });
    expect_out_of_range([&grid] { traceable_array_lab::checked_grid_at(grid, 2, 3, -1, 0); });
    expect_out_of_range([&grid] { traceable_array_lab::checked_grid_at(grid, 2, 3, 2, 0); });

    constexpr std::array growth_values{7, 3, 9, 3, 5};
    const auto events = traceable_array_lab::simulate_growth(growth_values);
    expect(events == std::vector{
        CapacityEvent{7, 1, 1, 0, 1},
        CapacityEvent{3, 2, 2, 1, 2},
        CapacityEvent{9, 3, 4, 2, 3},
        CapacityEvent{3, 4, 4, 0, 1},
        CapacityEvent{5, 5, 8, 4, 5},
    }, "capacity events");
    expect(traceable_array_lab::summarize_growth(events) == GrowthSummary{5, 7, 12, 8}, "growth summary");
    const auto reserved = traceable_array_lab::simulate_growth(growth_values, 5);
    for (const auto& event : reserved) {
        expect(event.copies == 0, "reserved growth should not copy");
    }

    expect(traceable_array_lab::build_text_report() ==
        "UTF-8 扫描\ntext：A工🧪\nbytes=8，code_points=3\nascii=1，multibyte=2", "text report");
    expect(traceable_array_lab::build_grid_report() ==
        "二维网格\nshape=2x3\ndata：1, 2, 3 / 4, 5, 6\nrow=1，col=2：value=6，flat_index=5\nrow=0：sum=6，visits=3", "grid report");
    expect(traceable_array_lab::build_capacity_report() ==
        "动态数组扩容\nappend | size | capacity | copies | steps\n7 | 1 | 1 | 0 | 1\n3 | 2 | 2 | 1 | 2\n9 | 3 | 4 | 2 | 3\n3 | 4 | 4 | 0 | 1\n5 | 5 | 8 | 4 | 5\ntotal_steps=12", "capacity report");
    return 0;
}
