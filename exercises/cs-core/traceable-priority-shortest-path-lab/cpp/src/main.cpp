#include "traceable_priority_shortest_path_lab/lab.hpp"

#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
  using namespace traceable_priority_shortest_path_lab;
  const std::string mode = argc == 1 ? "heap" : argv[1];
  if (argc > 2) {
    std::cerr << "unknown mode: " << mode << '\n';
    return 2;
  }
  if (mode == "heap") std::cout << build_heap_report() << '\n';
  else if (mode == "queue") std::cout << build_queue_report() << '\n';
  else if (mode == "dijkstra") std::cout << build_dijkstra_report() << '\n';
  else {
    std::cerr << "unknown mode: " << mode << '\n';
    return 2;
  }
  return 0;
}
