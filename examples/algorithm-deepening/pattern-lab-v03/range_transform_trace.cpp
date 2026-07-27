#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct RangeAdd {
  std::size_t left;
  std::size_t right;
  long long delta;
};

std::vector<long long> build_prefix(const std::vector<long long>& values) {
  std::vector<long long> prefix{0};
  for (const auto value : values) {
    prefix.push_back(prefix.back() + value);
  }
  return prefix;
}

long long range_sum(const std::vector<long long>& prefix, std::size_t left,
                    std::size_t right) {
  if (right < left || right >= prefix.size()) {
    throw std::out_of_range("invalid half-open range");
  }
  return prefix[right] - prefix[left];
}

std::pair<std::vector<long long>, std::vector<long long>> apply_range_adds(
    std::size_t length, const std::vector<RangeAdd>& updates) {
  std::vector<long long> difference(length + 1, 0);
  for (const auto& update : updates) {
    if (update.right < update.left || update.right > length) {
      throw std::out_of_range("invalid half-open update");
    }
    difference[update.left] += update.delta;
    difference[update.right] -= update.delta;
  }
  std::vector<long long> restored;
  long long running = 0;
  for (std::size_t index = 0; index < length; ++index) {
    running += difference[index];
    restored.push_back(running);
  }
  return {difference, restored};
}

void print_values(const std::vector<long long>& values) {
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) std::cout << ',';
    std::cout << values[index];
  }
}

int main() {
  const std::vector<long long> values{2, -1, 3, 5, 0};
  const auto prefix = build_prefix(values);
  const std::vector<RangeAdd> updates{{0, 3, 2}, {2, 5, -1}, {1, 4, 3}};
  const auto [difference, restored] = apply_range_adds(values.size(), updates);
  std::cout << "values=2,-1,3,5,0\n";
  std::cout << "prefix="; print_values(prefix); std::cout << '\n';
  std::cout << "sum[0:3)=" << range_sum(prefix, 0, 3) << '\n';
  std::cout << "sum[1:5)=" << range_sum(prefix, 1, 5) << '\n';
  std::cout << "sum[3:3)=" << range_sum(prefix, 3, 3) << '\n';
  std::cout << "updates=[0:3)+2,[2:5)-1,[1:4)+3\n";
  std::cout << "difference="; print_values(difference); std::cout << '\n';
  std::cout << "restored="; print_values(restored); std::cout << '\n';
  std::cout << "invariant=half-open-boundaries-cancel\n";
}
