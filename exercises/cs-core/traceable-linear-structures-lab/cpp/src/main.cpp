#include "traceable_linear_structures_lab/structures.hpp"

#include <iostream>
#include <string_view>

int main(int argc, char* argv[]) {
    if (argc > 2) {
        std::cerr << "用法：traceable_linear_structures_lab [linked|stack|queue]\n";
        return 2;
    }
    const std::string_view mode = argc == 1 ? "linked" : argv[1];
    if (mode == "linked") {
        std::cout << traceable_linear_structures_lab::build_linked_report() << '\n';
    } else if (mode == "stack") {
        std::cout << traceable_linear_structures_lab::build_stack_report() << '\n';
    } else if (mode == "queue") {
        std::cout << traceable_linear_structures_lab::build_queue_report() << '\n';
    } else {
        std::cerr << "用法：traceable_linear_structures_lab [linked|stack|queue]\n";
        return 2;
    }
    return 0;
}
