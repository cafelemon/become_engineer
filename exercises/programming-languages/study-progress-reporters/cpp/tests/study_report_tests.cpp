#include "study/study_report.hpp"

#include <cmath>
#include <iostream>
#include <string>
#include <vector>

namespace {

int failures{};

void expect_true(bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "FAILED: " << message << '\n';
        ++failures;
    }
}

void expect_close(double actual, double expected, const std::string& message) {
    constexpr double tolerance{0.000001};
    expect_true(std::abs(actual - expected) <= tolerance, message);
}

std::vector<std::string> names(const std::vector<study::StudyRecord>& records) {
    std::vector<std::string> result{};
    result.reserve(records.size());
    for (const study::StudyRecord& record : records) {
        result.push_back(record.course_name);
    }
    return result;
}

} // namespace

int main() {
    const std::vector<study::StudyRecord> records{study::sample_records()};
    const std::vector<std::string> original_names{names(records)};
    const study::StudySummary summary{study::summarize(records)};

    expect_close(summary.total_target_hours, 35.0, "total target hours");
    expect_close(summary.total_completed_hours, 30.5, "total completed hours");
    expect_true(summary.status_counts.at("已完成") == 2, "completed count");
    expect_true(summary.status_counts.at("进行中") == 2, "in-progress count");
    expect_true(summary.unique_tags.size() == 6, "duplicate tags should collapse");

    const study::StudySummary empty_summary{study::summarize({})};
    expect_close(empty_summary.total_target_hours, 0.0, "empty target total");
    expect_true(empty_summary.unique_tags.empty(), "empty tags");

    const std::vector<study::StudyRecord> sorted{study::sort_by_progress(records)};
    expect_true(
        names(sorted) == std::vector<std::string>{
            "C++ 核心", "工程复盘", "Python 起步", "算法练习"
        },
        "progress order and name tie-breaker"
    );
    expect_true(names(records) == original_names, "sorting must not mutate input");

    std::vector<study::StudyRecord> filtered{study::filter_by_tag(records, "基础")};
    expect_true(
        names(filtered) == std::vector<std::string>{
            "Python 起步", "C++ 核心", "算法练习"
        },
        "tag filter"
    );
    filtered.front().tags.push_back("changed");
    expect_true(
        records.front().tags.size() == 2,
        "filtered records must be independent copies"
    );
    expect_true(
        study::filter_by_tag(records, "不存在").empty(),
        "missing tag should return an empty vector"
    );

    const std::vector<study::StudyRecord> equal_progress{
        {"B", 2.0, 1.0, {}},
        {"A", 4.0, 2.0, {}},
    };
    expect_true(
        names(study::sort_by_progress(equal_progress)) ==
            std::vector<std::string>{"A", "B"},
        "equal progress should use name order"
    );

    const std::string expected{
        "学习进度报告\n"
        "总计划：35.0 小时\n"
        "总完成：30.5 小时\n"
        "总体进度：87.1%\n\n"
        "按进度排序：\n"
        "- C++ 核心：100.0%（已完成）\n"
        "- 工程复盘：100.0%（已完成）\n"
        "- Python 起步：75.0%（进行中）\n"
        "- 算法练习：50.0%（进行中）\n\n"
        "状态统计：\n"
        "- 已完成：2\n"
        "- 进行中：2\n"
        "唯一标签：cpp, python, 基础, 复盘, 工程, 算法\n"
        "标签[基础]：Python 起步, C++ 核心, 算法练习"
    };
    expect_true(study::build_report(records) == expected, "stable report output");

    if (failures == 0) {
        std::cout << "All study report tests passed.\n";
        return 0;
    }
    std::cerr << failures << " test(s) failed.\n";
    return 1;
}
