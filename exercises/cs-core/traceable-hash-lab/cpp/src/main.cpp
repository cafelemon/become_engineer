#include "traceable_hash_lab/hashing.hpp"

#include <iostream>
#include <string_view>

int main(const int argc, char* argv[]) {
    if (argc > 2) {
        std::cerr << "用法：traceable_hash_lab [hash|table|applications]\n";
        return 2;
    }
    const std::string_view mode = argc == 2 ? argv[1] : "hash";
    if (mode == "hash") {
        std::cout << traceable_hash_lab::build_hash_report() << '\n';
        return 0;
    }
    if (mode == "table") {
        std::cout << traceable_hash_lab::build_table_report() << '\n';
        return 0;
    }
    if (mode == "applications") {
        std::cout << traceable_hash_lab::build_applications_report() << '\n';
        return 0;
    }
    std::cerr << "用法：traceable_hash_lab [hash|table|applications]\n";
    return 2;
}
