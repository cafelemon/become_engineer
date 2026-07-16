#include "traceable_tree_traversal_lab/lab.hpp"

#include <iostream>
#include <string_view>

int main(int argc, char* argv[]) {
  using namespace traceable_tree_traversal_lab;
  const std::string_view mode = argc > 1 ? argv[1] : "shape";
  if (argc > 2 || (mode != "shape" && mode != "recursive" && mode != "frontier")) {
    std::cerr << "unknown mode: " << mode << '\n';
    return 2;
  }
  if (mode == "shape") {
    std::cout << build_shape_report() << '\n';
  } else if (mode == "recursive") {
    std::cout << build_recursive_report() << '\n';
  } else {
    std::cout << build_frontier_report() << '\n';
  }
  return 0;
}
