#include <algorithm>
#include <iostream>
#include <numeric>
#include <tuple>
#include <vector>

struct Result {
  int total;
  std::vector<int> chosen;
  std::vector<int> dp;
};

Result best_non_adjacent(const std::vector<int>& values) {
  std::vector<int> dp(values.size() + 1, 0);
  for (std::size_t prefix = 1; prefix <= values.size(); ++prefix) {
    const int skip = dp[prefix - 1];
    const int take = values[prefix - 1] + (prefix >= 2 ? dp[prefix - 2] : 0);
    dp[prefix] = std::max(skip, take);
  }
  std::vector<int> chosen;
  std::size_t prefix = values.size();
  while (prefix > 0) {
    const int skip = dp[prefix - 1];
    const int take = values[prefix - 1] + (prefix >= 2 ? dp[prefix - 2] : 0);
    if (take > skip) {
      chosen.push_back(static_cast<int>(prefix - 1));
      prefix = prefix >= 2 ? prefix - 2 : 0;
    } else {
      --prefix;
    }
  }
  std::reverse(chosen.begin(), chosen.end());
  return {dp.back(), chosen, dp};
}

std::pair<int, std::vector<int>> highest_first(const std::vector<int>& values) {
  std::vector<int> order(values.size());
  std::iota(order.begin(), order.end(), 0);
  std::sort(order.begin(), order.end(), [&](int left, int right) {
    return std::tie(values[right], left) < std::tie(values[left], right);
  });
  std::vector<bool> blocked(values.size(), false);
  std::vector<int> chosen;
  for (const int index : order) {
    if (values[index] <= 0 || blocked[index]) continue;
    chosen.push_back(index);
    blocked[index] = true;
    if (index > 0) blocked[index - 1] = true;
    if (index + 1 < static_cast<int>(values.size())) blocked[index + 1] = true;
  }
  std::sort(chosen.begin(), chosen.end());
  int total = 0;
  for (const int index : chosen) total += values[index];
  return {total, chosen};
}

void print_values(const std::vector<int>& values) {
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) std::cout << ',';
    std::cout << values[index];
  }
}

int main() {
  const std::vector<int> values{4, 5, 4, 1, 1};
  const auto result = best_non_adjacent(values);
  const auto greedy = highest_first(values);
  std::cout << "values=4,5,4,1,1\n";
  std::cout << "dp="; print_values(result.dp); std::cout << '\n';
  std::cout << "optimal=" << result.total << " chosen_indices="; print_values(result.chosen); std::cout << '\n';
  std::cout << "highest_first=" << greedy.first << " chosen_indices="; print_values(greedy.second); std::cout << '\n';
  std::cout << "transition=dp[i]=max(dp[i-1],dp[i-2]+value[i-1])\n";
  std::cout << "tie=skip-current\n";
  std::cout << "invariant=dp-prefix-optimum\n";
}
