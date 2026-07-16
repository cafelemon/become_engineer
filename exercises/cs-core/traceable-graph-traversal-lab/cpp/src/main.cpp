#include "traceable_graph_traversal_lab/lab.hpp"

#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
  using namespace traceable_graph_traversal_lab;
  const std::string mode = argc > 1 ? argv[1] : "graph";
  if (argc > 2) {
    std::cerr << "unknown mode: " << mode << '\n';
    return 2;
  }
  if (mode == "graph") {
    std::cout << build_graph_report() << '\n';
  } else if (mode == "bfs") {
    std::cout << build_bfs_report() << '\n';
  } else if (mode == "dfs") {
    std::cout << build_dfs_report() << '\n';
  } else {
    std::cerr << "unknown mode: " << mode << '\n';
    return 2;
  }
  return 0;
}
