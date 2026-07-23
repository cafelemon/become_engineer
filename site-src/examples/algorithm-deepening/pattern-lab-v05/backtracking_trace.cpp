#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <vector>

struct Result {
  std::vector<std::vector<long long>> solutions;
  std::size_t nodes = 0;
  std::size_t pruned = 0;
  bool path_restored = false;
};

void search(const std::vector<long long>& values, long long target,
            std::size_t start, long long total, std::vector<long long>& path,
            Result& result) {
  ++result.nodes;
  if (total == target) {
    result.solutions.push_back(path);
    return;
  }
  for (std::size_t index = start; index < values.size(); ++index) {
    if (index > start && values[index] == values[index - 1]) {
      ++result.pruned;
      continue;
    }
    if (total + values[index] > target) {
      result.pruned += values.size() - index;
      break;
    }
    path.push_back(values[index]);
    search(values, target, index + 1, total + values[index], path, result);
    path.pop_back();
  }
}

Result subset_sum_combinations(std::vector<long long> values, long long target) {
  if (target < 0) throw std::invalid_argument("target must be nonnegative");
  for (const auto value : values) {
    if (value <= 0) throw std::invalid_argument("values must be positive");
  }
  std::sort(values.begin(), values.end());
  Result result;
  std::vector<long long> path;
  search(values, target, 0, 0, path, result);
  result.path_restored = path.empty();
  return result;
}

int main() {
  const auto result = subset_sum_combinations({2, 3, 5, 6, 7}, 10);
  std::cout << "values=2,3,5,6,7 target=10\n";
  for (const auto& solution : result.solutions) {
    std::cout << "solution=";
    for (std::size_t index = 0; index < solution.size(); ++index) {
      if (index > 0) std::cout << ',';
      std::cout << solution[index];
    }
    std::cout << '\n';
  }
  std::cout << "solutions=" << result.solutions.size() << '\n';
  std::cout << "nodes=" << result.nodes
            << " pruned_candidates=" << result.pruned << '\n';
  std::cout << "path_after_search="
            << (result.path_restored ? "empty" : "dirty") << '\n';
  std::cout << "invariant=choose-search-undo\n";
}
