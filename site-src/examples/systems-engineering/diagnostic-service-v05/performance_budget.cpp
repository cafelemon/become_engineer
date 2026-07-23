#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace {

std::uint64_t nearest_rank(std::vector<std::uint64_t> values,
                           std::size_t percentile) {
  if (values.empty() || percentile == 0 || percentile > 100) {
    throw std::invalid_argument("percentile requires samples and range 1..100");
  }
  std::sort(values.begin(), values.end());
  const std::size_t rank =
      (percentile * values.size() + 99) / 100;  // ceil(p * n / 100)
  return values.at(rank - 1);
}

std::uint64_t diagnostic_work(std::uint64_t seed) {
  std::uint64_t value = seed;
  for (std::uint64_t step = 0; step < 32; ++step) {
    value = (value * 1664525U + 1013904223U) & 0xffffffffU;
  }
  return value;
}

}  // namespace

int main() {
  constexpr std::array<std::uint64_t, 20> kReplayLatencyUs{
      10, 12, 15, 18, 20, 22, 25, 27, 29, 30,
      30, 32, 35, 40, 45, 50, 60, 80, 120, 200};
  constexpr std::uint64_t kP95BudgetUs = 150;
  const std::vector<std::uint64_t> replay(kReplayLatencyUs.begin(),
                                          kReplayLatencyUs.end());
  const auto p50 = nearest_rank(replay, 50);
  const auto p95 = nearest_rank(replay, 95);
  const auto p99 = nearest_rank(replay, 99);

  constexpr std::size_t kWarmupIterations = 1000;
  constexpr std::size_t kMeasuredIterations = 2000;
  std::uint64_t checksum = 0;
  for (std::size_t index = 0; index < kWarmupIterations; ++index) {
    checksum ^= diagnostic_work(index);
  }
  const auto started = std::chrono::steady_clock::now();
  for (std::size_t index = 0; index < kMeasuredIterations; ++index) {
    checksum ^= diagnostic_work(index + kWarmupIterations);
  }
  const auto finished = std::chrono::steady_clock::now();
  const auto elapsed =
      std::chrono::duration_cast<std::chrono::nanoseconds>(finished - started);
  if (elapsed.count() < 0 || checksum == 0) {
    throw std::runtime_error("measurement sanity check failed");
  }

  std::cout << "replay_samples=20\n";
  std::cout << "percentile_method=nearest-rank\n";
  std::cout << "p50_us=" << p50 << '\n';
  std::cout << "p95_us=" << p95 << '\n';
  std::cout << "p99_us=" << p99 << '\n';
  std::cout << "budget_p95_us=150 result="
            << (p95 <= kP95BudgetUs ? "pass" : "fail") << '\n';
  std::cout << "measurement_clock=steady_clock\n";
  std::cout << "warmup_iterations=1000\n";
  std::cout << "measurement_samples=2000\n";
  std::cout << "elapsed=observed-not-asserted\n";
  return p95 <= kP95BudgetUs ? 0 : 2;
}
