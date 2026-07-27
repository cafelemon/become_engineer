#include <deque>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <vector>

struct GreaterResult {
  std::vector<std::optional<long long>> answers;
  std::size_t resolved;
  std::size_t unresolved;
};

GreaterResult next_strictly_greater(const std::vector<long long>& values) {
  std::vector<std::optional<long long>> answers(values.size());
  std::vector<std::size_t> stack;
  std::size_t resolved = 0;
  for (std::size_t index = 0; index < values.size(); ++index) {
    while (!stack.empty() && values[stack.back()] < values[index]) {
      answers[stack.back()] = values[index];
      stack.pop_back();
      ++resolved;
    }
    stack.push_back(index);
  }
  return {answers, resolved, stack.size()};
}

struct MaximumResult {
  std::vector<long long> maxima;
  std::size_t back_pruned;
  std::size_t expired;
};

MaximumResult sliding_maximum(const std::vector<long long>& values,
                              std::size_t width) {
  if (width == 0) throw std::invalid_argument("width must be positive");
  if (width > values.size()) return {};
  std::deque<std::size_t> candidates;
  MaximumResult result{};
  for (std::size_t index = 0; index < values.size(); ++index) {
    while (!candidates.empty() && candidates.front() + width <= index) {
      candidates.pop_front();
      ++result.expired;
    }
    while (!candidates.empty() &&
           values[candidates.back()] <= values[index]) {
      candidates.pop_back();
      ++result.back_pruned;
    }
    candidates.push_back(index);
    if (index + 1 >= width) {
      result.maxima.push_back(values[candidates.front()]);
    }
  }
  return result;
}

int main() {
  const std::vector<long long> values{2, 1, 2, 4, 3};
  const auto greater = next_strictly_greater(values);
  const auto maximum = sliding_maximum(values, 3);
  std::cout << "values=2,1,2,4,3\nnext_strictly_greater=";
  for (std::size_t index = 0; index < greater.answers.size(); ++index) {
    if (index > 0) std::cout << ',';
    if (greater.answers[index].has_value()) std::cout << *greater.answers[index];
    else std::cout << "none";
  }
  std::cout << "\nstack_resolved=" << greater.resolved
            << " unresolved=" << greater.unresolved << '\n';
  std::cout << "window_width=3\nwindow_maxima=";
  for (std::size_t index = 0; index < maximum.maxima.size(); ++index) {
    if (index > 0) std::cout << ',';
    std::cout << maximum.maxima[index];
  }
  std::cout << "\ndeque_back_pruned=" << maximum.back_pruned
            << " expired=" << maximum.expired << '\n';
  std::cout << "invariant=dominated-candidates-never-return\n";
}
