#include "study/study_status.hpp"

#include <cmath>
#include <iostream>
#include <string>

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

} // namespace

int main() {
    expect_close(study::calculate_progress(10.0, 7.5), 0.75, "normal progress");
    expect_close(study::calculate_progress(10.0, 12.5), 1.0, "clamped progress");
    expect_close(study::calculate_progress(0.0, 1.0), 0.0, "safe invalid plan");
    expect_true(study::build_status(10.0, 7.5) == "进行中", "in progress");
    expect_true(study::build_status(10.0, 10.0) == "已完成", "completed");
    expect_true(study::validate_input("", 10.0, 1.0) == "输入错误：姓名不能为空。", "empty learner");
    expect_true(study::validate_input("Lin", 0.0, 0.0) == "输入错误：计划学习时间必须大于 0。", "zero plan");
    expect_true(study::validate_input("Lin", 10.0, -1.0) == "输入错误：已完成时间不能小于 0。", "negative completed");

    if (failures == 0) {
        std::cout << "All study status tests passed.\n";
        return 0;
    }
    return 1;
}
