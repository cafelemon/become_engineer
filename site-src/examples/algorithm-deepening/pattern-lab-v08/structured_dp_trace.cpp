#include <algorithm>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

std::vector<int> knapsack(const std::vector<int>& weights, const std::vector<int>& values,
                          int capacity, bool descending) {
  if (weights.size() != values.size() || capacity < 0) throw std::invalid_argument("invalid knapsack input");
  for (const int weight : weights) if (weight <= 0) throw std::invalid_argument("invalid knapsack input");
  std::vector<int> dp(static_cast<std::size_t>(capacity + 1), 0);
  for (std::size_t item = 0; item < weights.size(); ++item) {
    if (descending) {
      for (int current = capacity; current >= weights[item]; --current) {
        dp[current] = std::max(dp[current], dp[current - weights[item]] + values[item]);
      }
    } else {
      for (int current = weights[item]; current <= capacity; ++current) {
        dp[current] = std::max(dp[current], dp[current - weights[item]] + values[item]);
      }
    }
  }
  return dp;
}

std::pair<long long, std::string> matrix_chain(const std::vector<int>& dimensions) {
  if (dimensions.size() < 2) throw std::invalid_argument("invalid matrix dimensions");
  for (const int dimension : dimensions) if (dimension <= 0) throw std::invalid_argument("invalid matrix dimensions");
  const std::size_t count = dimensions.size() - 1;
  std::vector<std::vector<long long>> cost(count, std::vector<long long>(count, 0));
  std::vector<std::vector<std::size_t>> split(count, std::vector<std::size_t>(count, 0));
  for (std::size_t length = 2; length <= count; ++length) {
    for (std::size_t left = 0; left + length <= count; ++left) {
      const std::size_t right = left + length - 1;
      long long best = std::numeric_limits<long long>::max();
      for (std::size_t middle = left; middle < right; ++middle) {
        const long long candidate = cost[left][middle] + cost[middle + 1][right]
          + static_cast<long long>(dimensions[left]) * dimensions[middle + 1] * dimensions[right + 1];
        if (candidate < best) {
          best = candidate;
          split[left][right] = middle;
        }
      }
      cost[left][right] = best;
    }
  }
  const auto build = [&](const auto& self, std::size_t left, std::size_t right) -> std::string {
    if (left == right) return "A" + std::to_string(left + 1);
    const std::size_t middle = split[left][right];
    return "(" + self(self, left, middle) + self(self, middle + 1, right) + ")";
  };
  return {cost[0][count - 1], build(build, 0, count - 1)};
}

void print_values(const std::vector<int>& values) {
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) std::cout << ',';
    std::cout << values[index];
  }
}

int main() {
  const auto table = knapsack({2,3,4,5}, {3,4,5,8}, 7, true);
  const int correct_single = knapsack({2}, {3}, 4, true).back();
  const int wrong_single = knapsack({2}, {3}, 4, false).back();
  const auto matrix = matrix_chain({10,30,5,60});
  std::cout << "knapsack_weights=2,3,4,5 values=3,4,5,8 capacity=7\n";
  std::cout << "knapsack_dp="; print_values(table); std::cout << '\n';
  std::cout << "knapsack_optimal=" << table.back() << '\n';
  std::cout << "forward_single_item=" << wrong_single << " correct_single_item=" << correct_single << '\n';
  std::cout << "matrix_dims=10,30,5,60\n";
  std::cout << "matrix_cost=" << matrix.first << " order=" << matrix.second << '\n';
  std::cout << "orders=capacity-descending,interval-length-ascending\n";
  std::cout << "invariants=item-used-at-most-once,subintervals-ready\n";
}

