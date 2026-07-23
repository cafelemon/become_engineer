#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Step {
  std::size_t left;
  std::size_t right;
  long long total;
  std::string action;
};

struct Result {
  std::optional<std::pair<std::size_t, std::size_t>> pair;
  std::vector<Step> steps;
};

Result find_pair(const std::vector<long long>& values, long long target) {
  for (std::size_t index = 1; index < values.size(); ++index) {
    if (values[index - 1] > values[index]) {
      throw std::invalid_argument("values must be sorted");
    }
  }
  if (values.size() < 2) {
    return {};
  }
  std::size_t left = 0;
  std::size_t right = values.size() - 1;
  Result result;
  while (left < right) {
    const long long total = values[left] + values[right];
    if (total == target) {
      result.steps.push_back({left, right, total, "match"});
      result.pair = std::pair{left, right};
      return result;
    }
    if (total < target) {
      result.steps.push_back({left, right, total, "left++"});
      ++left;
    } else {
      result.steps.push_back({left, right, total, "right--"});
      --right;
    }
  }
  return result;
}

int main() {
  const std::vector<long long> values{1, 2, 3, 4, 6, 8};
  const auto result = find_pair(values, 8);
  std::cout << "input=1,2,3,4,6,8 target=8\n";
  for (const auto& step : result.steps) {
    std::cout << "step left=" << step.left << " right=" << step.right
              << " sum=" << step.total << " action=" << step.action << '\n';
  }
  if (!result.pair.has_value()) {
    std::cout << "result=not-found\n";
  } else {
    const auto [left, right] = *result.pair;
    std::cout << "result=" << left << ',' << right << " values=" << values[left]
              << ',' << values[right] << '\n';
  }
  std::cout << "invariant=outside-pairs-eliminated\n";
}
