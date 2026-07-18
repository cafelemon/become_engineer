#include <iomanip>
#include <iostream>
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

int main() {
    std::string learner{};
    double planned_hours{};
    double completed_hours{};

    std::cout << "请输入学习者姓名：";
    std::getline(std::cin, learner);
    std::cout << "请输入计划学习时间：";
    std::cin >> planned_hours;
    std::cout << "请输入已完成时间：";
    std::cin >> completed_hours;

    if (!std::cin) {
        std::cerr << "输入错误：学习时间必须是数字。\n";
        return 1;
    }

    const std::string error_message{
        study::validate_input(learner, planned_hours, completed_hours)
    };
    if (!error_message.empty()) {
        std::cerr << error_message << '\n';
        return 1;
    }

    study::print_status_card(learner, planned_hours, completed_hours);
    return 0;
}

namespace study {

std::string validate_input(
    const std::string& learner,
    double planned_hours,
    double completed_hours
) {
    if (learner.empty()) {
        return "输入错误：姓名不能为空。";
    }
    if (planned_hours <= 0.0) {
        return "输入错误：计划学习时间必须大于 0。";
    }
    if (completed_hours < 0.0) {
        return "输入错误：已完成时间不能小于 0。";
    }
    return "";
}

double calculate_progress(double planned_hours, double completed_hours) {
    const double raw_progress{completed_hours / planned_hours};
    return raw_progress > 1.0 ? 1.0 : raw_progress;
}

std::string build_status(double planned_hours, double completed_hours) {
    return completed_hours >= planned_hours ? "已完成" : "进行中";
}

void print_status_card(
    const std::string& learner,
    double planned_hours,
    double completed_hours
) {
    const double displayed_progress{
        calculate_progress(planned_hours, completed_hours)
    };
    const std::string status{build_status(planned_hours, completed_hours)};

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "\n学习状态卡\n";
    std::cout << "姓名：" << learner << '\n';
    std::cout << "计划：" << planned_hours << " 小时\n";
    std::cout << "完成：" << completed_hours << " 小时\n";
    std::cout << "进度：" << displayed_progress * 100.0 << "%\n";
    std::cout << "状态：" << status << '\n';
}

} // namespace study
