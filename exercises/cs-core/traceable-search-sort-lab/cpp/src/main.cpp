#include "traceable_search_sort_lab/lab.hpp"

#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
  using traceable_search_sort_lab::build_elementary_report;
  using traceable_search_sort_lab::build_merge_report;
  using traceable_search_sort_lab::build_search_report;

  if (argc > 2) {
    std::cerr << "用法：traceable_search_sort_lab [search|elementary|merge]\n";
    return 2;
  }
  const std::string mode = argc == 2 ? argv[1] : "search";
  if (mode == "search") {
    std::cout << build_search_report() << '\n';
  } else if (mode == "elementary") {
    std::cout << build_elementary_report() << '\n';
  } else if (mode == "merge") {
    std::cout << build_merge_report() << '\n';
  } else {
    std::cerr << "用法：traceable_search_sort_lab [search|elementary|merge]\n";
    return 2;
  }
  return 0;
}
