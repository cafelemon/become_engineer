#include "traceable_array_lab/lab.hpp"

#include <array>
#include <cstdint>
#include <limits>
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

void validate_grid_shape(
    std::span<const int> values,
    std::size_t rows,
    std::size_t columns
) {
    if (rows != 0 && columns > std::numeric_limits<std::size_t>::max() / rows) {
        throw std::invalid_argument("grid shape multiplication overflow");
    }
    if (rows * columns != values.size()) {
        throw std::invalid_argument("grid shape does not match data length");
    }
}

std::size_t checked_grid_index(
    std::span<const int> values,
    std::size_t rows,
    std::size_t columns,
    std::ptrdiff_t row,
    std::ptrdiff_t column
) {
    validate_grid_shape(values, rows, columns);
    if (row < 0 || column < 0 || static_cast<std::size_t>(row) >= rows ||
        static_cast<std::size_t>(column) >= columns) {
        throw std::out_of_range("grid coordinate outside boundary");
    }
    return static_cast<std::size_t>(row) * columns +
           static_cast<std::size_t>(column);
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

Utf8Trace analyze_utf8(std::string_view data) {
    std::size_t index = 0;
    std::size_t code_points = 0;
    std::size_t ascii = 0;
    while (index < data.size()) {
        const auto lead = static_cast<unsigned char>(data[index]);
        if (lead <= 0x7FU) {
            ++ascii;
            ++code_points;
            ++index;
            continue;
        }

        std::size_t width = 0;
        std::uint32_t code_point = 0;
        std::uint32_t minimum = 0;
        if (lead >= 0xC2U && lead <= 0xDFU) {
            width = 2;
            code_point = lead & 0x1FU;
            minimum = 0x80U;
        } else if (lead >= 0xE0U && lead <= 0xEFU) {
            width = 3;
            code_point = lead & 0x0FU;
            minimum = 0x800U;
        } else if (lead >= 0xF0U && lead <= 0xF4U) {
            width = 4;
            code_point = lead & 0x07U;
            minimum = 0x10000U;
        } else {
            throw std::invalid_argument("invalid UTF-8 leading byte");
        }
        if (data.size() - index < width) {
            throw std::invalid_argument("truncated UTF-8 sequence");
        }
        for (std::size_t offset = 1; offset < width; ++offset) {
            const auto continuation = static_cast<unsigned char>(data[index + offset]);
            if (continuation < 0x80U || continuation > 0xBFU) {
                throw std::invalid_argument("invalid UTF-8 continuation byte");
            }
            code_point = (code_point << 6U) | (continuation & 0x3FU);
        }
        if (code_point < minimum ||
            (code_point >= 0xD800U && code_point <= 0xDFFFU) ||
            code_point > 0x10FFFFU) {
            throw std::invalid_argument("invalid UTF-8 code point");
        }
        ++code_points;
        index += width;
    }
    return Utf8Trace{data.size(), code_points, ascii, code_points - ascii};
}

GridCell checked_grid_at(
    std::span<const int> values,
    std::size_t rows,
    std::size_t columns,
    std::ptrdiff_t row,
    std::ptrdiff_t column
) {
    const auto index = checked_grid_index(values, rows, columns, row, column);
    return GridCell{values[index], index};
}

RowTrace sum_grid_row(
    std::span<const int> values,
    std::size_t rows,
    std::size_t columns,
    std::ptrdiff_t row
) {
    validate_grid_shape(values, rows, columns);
    if (row < 0 || static_cast<std::size_t>(row) >= rows) {
        throw std::out_of_range("grid row outside boundary");
    }
    const auto start = static_cast<std::size_t>(row) * columns;
    int total = 0;
    for (std::size_t offset = 0; offset < columns; ++offset) {
        total += values[start + offset];
    }
    return RowTrace{total, columns};
}

std::vector<CapacityEvent> simulate_growth(
    std::span<const int> values,
    std::size_t initial_capacity
) {
    std::size_t size = 0;
    std::size_t capacity = initial_capacity;
    std::vector<CapacityEvent> events;
    events.reserve(values.size());
    for (const auto value : values) {
        std::size_t copies = 0;
        if (size == capacity) {
            copies = size;
            if (capacity == 0) {
                capacity = 1;
            } else {
                if (capacity > std::numeric_limits<std::size_t>::max() / 2U) {
                    throw std::overflow_error("simulated capacity overflow");
                }
                capacity *= 2U;
            }
        }
        ++size;
        events.push_back(CapacityEvent{value, size, capacity, copies, copies + 1U});
    }
    return events;
}

GrowthSummary summarize_growth(std::span<const CapacityEvent> events) {
    std::size_t total_copies = 0;
    std::size_t total_steps = 0;
    for (const auto& event : events) {
        total_copies += event.copies;
        total_steps += event.steps;
    }
    return GrowthSummary{
        events.size(),
        total_copies,
        total_steps,
        events.empty() ? 0U : events.back().capacity,
    };
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

std::string build_text_report() {
    constexpr std::string_view data{"A\xE5\xB7\xA5\xF0\x9F\xA7\xAA"};
    const auto trace = analyze_utf8(data);
    std::ostringstream output;
    output << "UTF-8 扫描\n"
           << "text：A工🧪\n"
           << "bytes=" << trace.byte_count
           << "，code_points=" << trace.code_point_count << '\n'
           << "ascii=" << trace.ascii_count
           << "，multibyte=" << trace.multibyte_count;
    return output.str();
}

std::string build_grid_report() {
    constexpr std::array values{1, 2, 3, 4, 5, 6};
    const auto cell = checked_grid_at(values, 2, 3, 1, 2);
    const auto row = sum_grid_row(values, 2, 3, 0);
    std::ostringstream output;
    output << "二维网格\n"
           << "shape=2x3\n"
           << "data：1, 2, 3 / 4, 5, 6\n"
           << "row=1，col=2：value=" << cell.value
           << "，flat_index=" << cell.flat_index << '\n'
           << "row=0：sum=" << row.total << "，visits=" << row.visits;
    return output.str();
}

std::string build_capacity_report() {
    constexpr std::array values{7, 3, 9, 3, 5};
    const auto events = simulate_growth(values);
    const auto summary = summarize_growth(events);
    std::ostringstream output;
    output << "动态数组扩容\n"
           << "append | size | capacity | copies | steps\n";
    for (const auto& event : events) {
        output << event.value << " | " << event.size << " | "
               << event.capacity << " | " << event.copies << " | "
               << event.steps << '\n';
    }
    output << "total_steps=" << summary.total_steps;
    return output.str();
}

}  // namespace traceable_array_lab
