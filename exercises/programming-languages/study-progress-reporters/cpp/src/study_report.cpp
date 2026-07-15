#include "study/study_report.hpp"

#include <algorithm>
#include <iomanip>
#include <iterator>
#include <numeric>
#include <sstream>

namespace study {

double calculate_progress(const StudyRecord& record) {
    if (record.target_hours <= 0.0) {
        return 0.0;
    }
    const double raw_progress{record.completed_hours / record.target_hours};
    return std::clamp(raw_progress, 0.0, 1.0);
}

std::string build_status(const StudyRecord& record) {
    return record.completed_hours >= record.target_hours ? "已完成" : "进行中";
}

StudySummary summarize(const std::vector<StudyRecord>& records) {
    StudySummary summary{
        std::accumulate(
            records.begin(), records.end(), 0.0,
            [](double total, const StudyRecord& record) {
                return total + record.target_hours;
            }
        ),
        std::accumulate(
            records.begin(), records.end(), 0.0,
            [](double total, const StudyRecord& record) {
                return total + record.completed_hours;
            }
        ),
        {
            {"已完成", static_cast<std::size_t>(std::count_if(
                records.begin(), records.end(),
                [](const StudyRecord& record) {
                    return build_status(record) == "已完成";
                }
            ))},
            {"进行中", static_cast<std::size_t>(std::count_if(
                records.begin(), records.end(),
                [](const StudyRecord& record) {
                    return build_status(record) == "进行中";
                }
            ))},
        },
        {},
    };

    for (const StudyRecord& record : records) {
        summary.unique_tags.insert(record.tags.begin(), record.tags.end());
    }
    return summary;
}

std::vector<StudyRecord> sort_by_progress(std::vector<StudyRecord> records) {
    std::sort(
        records.begin(), records.end(),
        [](const StudyRecord& left, const StudyRecord& right) {
            const double left_progress{calculate_progress(left)};
            const double right_progress{calculate_progress(right)};
            if (left_progress != right_progress) {
                return left_progress > right_progress;
            }
            return left.course_name < right.course_name;
        }
    );
    return records;
}

std::vector<StudyRecord> filter_by_tag(
    const std::vector<StudyRecord>& records,
    const std::string& tag
) {
    std::vector<StudyRecord> result{};
    result.reserve(records.size());
    std::copy_if(
        records.begin(), records.end(), std::back_inserter(result),
        [&tag](const StudyRecord& record) {
            return std::find(record.tags.begin(), record.tags.end(), tag) !=
                record.tags.end();
        }
    );
    return result;
}

namespace {

std::string join_names(const std::vector<StudyRecord>& records) {
    if (records.empty()) {
        return "无";
    }
    std::ostringstream output{};
    for (auto iterator = records.begin(); iterator != records.end(); ++iterator) {
        if (iterator != records.begin()) {
            output << ", ";
        }
        output << iterator->course_name;
    }
    return output.str();
}

std::string join_tags(const std::set<std::string>& tags) {
    if (tags.empty()) {
        return "无";
    }
    std::ostringstream output{};
    for (auto iterator = tags.begin(); iterator != tags.end(); ++iterator) {
        if (iterator != tags.begin()) {
            output << ", ";
        }
        output << *iterator;
    }
    return output.str();
}

} // namespace

std::string build_report(const std::vector<StudyRecord>& records) {
    const StudySummary summary{summarize(records)};
    const std::vector<StudyRecord> sorted_records{sort_by_progress(records)};
    const std::vector<StudyRecord> basic_records{filter_by_tag(records, "基础")};
    const double overall_progress{
        summary.total_target_hours > 0.0
            ? std::clamp(
                summary.total_completed_hours / summary.total_target_hours,
                0.0, 1.0
            )
            : 0.0
    };

    std::vector<double> progresses{};
    progresses.reserve(sorted_records.size());
    std::transform(
        sorted_records.begin(), sorted_records.end(),
        std::back_inserter(progresses),
        [](const StudyRecord& record) { return calculate_progress(record); }
    );

    std::ostringstream output{};
    output << std::fixed << std::setprecision(1);
    output << "学习进度报告\n";
    output << "总计划：" << summary.total_target_hours << " 小时\n";
    output << "总完成：" << summary.total_completed_hours << " 小时\n";
    output << "总体进度：" << overall_progress * 100.0 << "%\n\n";
    output << "按进度排序：\n";
    for (std::size_t index{}; index < sorted_records.size(); ++index) {
        output << "- " << sorted_records[index].course_name << "："
               << progresses[index] * 100.0 << "%（"
               << build_status(sorted_records[index]) << "）\n";
    }
    output << "\n状态统计：\n";
    for (const auto& [status, count] : summary.status_counts) {
        output << "- " << status << "：" << count << '\n';
    }
    output << "唯一标签：" << join_tags(summary.unique_tags) << '\n';
    output << "标签[基础]：" << join_names(basic_records);
    return output.str();
}

std::vector<StudyRecord> sample_records() {
    return {
        {"Python 起步", 10.0, 7.5, {"python", "基础"}},
        {"C++ 核心", 12.0, 12.0, {"cpp", "基础"}},
        {"算法练习", 8.0, 4.0, {"算法", "基础", "基础"}},
        {"工程复盘", 5.0, 7.0, {"工程", "复盘"}},
    };
}

} // namespace study
