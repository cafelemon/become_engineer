#include <iostream>
#include <string>

int main() {
    const std::string course{"C++ 起步"};
    const int planned_hours{5};

    std::cout << "学习状态卡\n";
    std::cout << "课程：" << course << '\n';
    std::cout << "本周计划：" << planned_hours << " 小时\n";
    return 0;
}
