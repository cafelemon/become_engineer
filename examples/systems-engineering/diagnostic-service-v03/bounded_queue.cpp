#include <condition_variable>
#include <cstddef>
#include <deque>
#include <iostream>
#include <mutex>
#include <optional>
#include <sstream>
#include <thread>
#include <vector>

template <typename T>
class BoundedQueue {
 public:
  explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}

  bool push(T value) {
    std::unique_lock lock(mutex_);
    if (closed_) return false;
    if (items_.size() >= capacity_) {
      ++waiting_producers_;
      state_changed_.notify_all();
      not_full_.wait(lock, [this] { return items_.size() < capacity_ || closed_; });
      --waiting_producers_;
    }
    if (closed_) return false;
    items_.push_back(std::move(value));
    not_empty_.notify_one();
    return true;
  }

  std::optional<T> pop() {
    std::unique_lock lock(mutex_);
    not_empty_.wait(lock, [this] { return !items_.empty() || closed_; });
    if (items_.empty()) return std::nullopt;
    T value = std::move(items_.front());
    items_.pop_front();
    not_full_.notify_one();
    return value;
  }

  void close() {
    std::lock_guard lock(mutex_);
    closed_ = true;
    not_empty_.notify_all();
    not_full_.notify_all();
    state_changed_.notify_all();
  }

  void wait_for_blocked_producer() {
    std::unique_lock lock(mutex_);
    state_changed_.wait(lock, [this] { return waiting_producers_ > 0; });
  }

  [[nodiscard]] std::size_t waiting_producers() const {
    std::lock_guard lock(mutex_);
    return waiting_producers_;
  }

 private:
  const std::size_t capacity_;
  mutable std::mutex mutex_;
  std::condition_variable not_empty_;
  std::condition_variable not_full_;
  std::condition_variable state_changed_;
  std::deque<T> items_;
  std::size_t waiting_producers_ = 0;
  bool closed_ = false;
};

int main() {
  BoundedQueue<int> queue(1);
  std::vector<int> processed;
  std::mutex processed_mutex;
  int accepted = 0;

  std::thread producer([&] {
    for (int value : {1, 2, 3}) {
      if (queue.push(value)) ++accepted;
    }
  });

  queue.wait_for_blocked_producer();
  const std::size_t blocked = queue.waiting_producers();

  std::thread consumer([&] {
    while (const auto value = queue.pop()) {
      std::lock_guard lock(processed_mutex);
      processed.push_back(*value);
    }
  });

  producer.join();
  queue.close();
  consumer.join();
  const bool rejected_after_close = !queue.push(4);
  const bool closed_after_drain = !queue.pop().has_value();

  std::ostringstream order;
  for (std::size_t index = 0; index < processed.size(); ++index) {
    if (index) order << ',';
    order << processed[index];
  }

  std::cout << "capacity=1\n";
  std::cout << "backpressure=observed waiting_producers=" << blocked << '\n';
  std::cout << "accepted=" << accepted << " processed=" << processed.size() << '\n';
  std::cout << "order=" << order.str() << '\n';
  std::cout << "push_after_close=" << (rejected_after_close ? "rejected" : "accepted") << '\n';
  std::cout << "pop_after_drain=" << (closed_after_drain ? "closed" : "value") << '\n';
  std::cout << "invariant="
            << (accepted == static_cast<int>(processed.size()) ? "accepted-equals-processed" : "violated")
            << '\n';
  return accepted == 3 && processed == std::vector<int>({1, 2, 3}) &&
                 rejected_after_close && closed_after_drain
             ? 0
             : 1;
}
