#include "study/study_report.hpp"

#include <iostream>

int main() {
    std::cout << study::build_report(study::sample_records()) << '\n';
    return 0;
}
