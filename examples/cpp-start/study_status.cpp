#include <iostream>
#include <string>

int main() {
    std::cout << "请输入姓名：";
    std::string learner{};
    if (!std::getline(std::cin, learner) || learner.empty()) {
        std::cerr << "姓名不能为空\n";
        return 1;
    }

    std::cout << "请输入本周计划小时：";
    double planned_hours{};
    if (!(std::cin >> planned_hours)) {
        std::cerr << "计划小时必须是数字\n";
        return 1;
    }
    if (planned_hours <= 0.0) {
        std::cerr << "计划小时必须大于 0\n";
        return 1;
    }

    const std::string course{"C++ 起步"};
    const bool finished{false};
    std::cout << "学习状态卡\n";
    std::cout << "姓名：" << learner << '\n';
    std::cout << "课程：" << course << '\n';
    std::cout << "本周计划：" << planned_hours << " 小时\n";
    std::cout << "是否完成：" << std::boolalpha << finished << '\n';
    return 0;
}
