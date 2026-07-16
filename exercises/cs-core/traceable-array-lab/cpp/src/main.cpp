#include "traceable_array_lab/lab.hpp"

#include <iostream>
#include <string_view>

int main(int argc, char* argv[]) {
    if (argc > 2) {
        std::cerr << "用法：traceable_array_lab [baseline|text|grid|capacity]\n";
        return 2;
    }
    const std::string_view mode = argc == 1 ? "baseline" : argv[1];
    if (mode == "baseline") {
        std::cout << traceable_array_lab::build_report() << '\n';
    } else if (mode == "text") {
        std::cout << traceable_array_lab::build_text_report() << '\n';
    } else if (mode == "grid") {
        std::cout << traceable_array_lab::build_grid_report() << '\n';
    } else if (mode == "capacity") {
        std::cout << traceable_array_lab::build_capacity_report() << '\n';
    } else {
        std::cerr << "用法：traceable_array_lab [baseline|text|grid|capacity]\n";
        return 2;
    }
    return 0;
}
