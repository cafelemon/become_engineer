#ifndef BECOME_ENGINEER_STUDY_STUDY_STATUS_HPP
#define BECOME_ENGINEER_STUDY_STUDY_STATUS_HPP

#include <string>

namespace study {

std::string validate_input(
    const std::string& learner,
    double planned_hours,
    double completed_hours
);
double calculate_progress(double planned_hours, double completed_hours);
std::string build_status(double planned_hours, double completed_hours);
void print_status_card(
    const std::string& learner,
    double planned_hours,
    double completed_hours
);

} // namespace study

#endif
