#ifndef BECOME_ENGINEER_STUDY_STUDY_REPORT_HPP
#define BECOME_ENGINEER_STUDY_STUDY_REPORT_HPP

#include <cstddef>
#include <filesystem>
#include <map>
#include <set>
#include <string>
#include <vector>

namespace study {

struct StudyRecord {
    std::string course_name;
    double target_hours;
    double completed_hours;
    std::vector<std::string> tags;
};

struct StudySummary {
    double total_target_hours;
    double total_completed_hours;
    std::map<std::string, std::size_t> status_counts;
    std::set<std::string> unique_tags;
};

double calculate_progress(const StudyRecord& record);
std::string build_status(const StudyRecord& record);
StudySummary summarize(const std::vector<StudyRecord>& records);
std::vector<StudyRecord> sort_by_progress(std::vector<StudyRecord> records);
std::vector<StudyRecord> filter_by_tag(
    const std::vector<StudyRecord>& records,
    const std::string& tag
);
void add_completed_hours(StudyRecord& record, double additional_hours);
StudyRecord* find_record_by_name(
    std::vector<StudyRecord>& records,
    const std::string& course_name
);
bool write_audit_snapshot(
    const std::vector<StudyRecord>& records,
    const std::filesystem::path& output_path
);
std::string build_report(const std::vector<StudyRecord>& records);
std::vector<StudyRecord> sample_records();

} // namespace study

#endif
