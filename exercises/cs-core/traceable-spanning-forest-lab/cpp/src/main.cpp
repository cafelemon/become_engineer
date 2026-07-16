#include "traceable_spanning_forest_lab/lab.hpp"
#include <iostream>
#include <string>
int main(int argc, char* argv[]) {
  using namespace traceable_spanning_forest_lab;
  const std::string mode = argc == 1 ? "dsu" : argv[1];
  if (argc > 2) { std::cerr << "unknown mode: " << mode << '\n'; return 2; }
  if (mode == "dsu") std::cout << build_dsu_report() << '\n';
  else if (mode == "kruskal") std::cout << build_kruskal_report() << '\n';
  else if (mode == "prim") std::cout << build_prim_report() << '\n';
  else { std::cerr << "unknown mode: " << mode << '\n'; return 2; }
  return 0;
}

