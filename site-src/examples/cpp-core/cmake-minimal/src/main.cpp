#include "study/study_status.hpp"

#include <iostream>
#include <string>

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
    const std::string error{
        study::validate_input(learner, planned_hours, completed_hours)
    };
    if (!error.empty()) {
        std::cerr << error << '\n';
        return 1;
    }

    study::print_status_card(learner, planned_hours, completed_hours);
    return 0;
}
