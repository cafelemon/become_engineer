#include <array>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

struct Window {
  std::size_t left;
  std::size_t right;
  std::string text;
};

struct Result {
  bool found = false;
  Window best{};
  std::vector<Window> improvements;
  std::size_t expands = 0;
  std::size_t shrinks = 0;
};

Result minimum_cover(const std::string& text, const std::string& need) {
  if (need.empty()) {
    throw std::invalid_argument("need must not be empty");
  }
  std::array<int, 256> required{};
  std::array<int, 256> current{};
  std::size_t required_kinds = 0;
  for (const unsigned char character : need) {
    if (required[character]++ == 0) {
      ++required_kinds;
    }
  }

  Result result;
  std::size_t formed = 0;
  std::size_t left = 0;
  for (std::size_t right = 0; right < text.size(); ++right) {
    const auto character = static_cast<unsigned char>(text[right]);
    ++current[character];
    if (required[character] > 0 &&
        current[character] == required[character]) {
      ++formed;
    }
    ++result.expands;

    while (formed == required_kinds) {
      const std::size_t length = right - left + 1;
      if (!result.found || length < result.best.text.size()) {
        result.found = true;
        result.best = {left, right, text.substr(left, length)};
        result.improvements.push_back(result.best);
      }
      const auto removed = static_cast<unsigned char>(text[left]);
      --current[removed];
      ++left;
      ++result.shrinks;
      if (required[removed] > 0 && current[removed] < required[removed]) {
        --formed;
      }
    }
  }
  return result;
}

int main() {
  const auto result = minimum_cover("ADOBECODEBANC", "ABC");
  std::cout << "input=ADOBECODEBANC need=ABC\n";
  std::cout << "required_kinds=3\n";
  for (const auto& item : result.improvements) {
    std::cout << "best=" << item.left << ':' << item.right
              << " text=" << item.text << '\n';
  }
  if (!result.found) {
    std::cout << "result=not-found\n";
  } else {
    std::cout << "result=" << result.best.left << ':' << result.best.right
              << " text=" << result.best.text << '\n';
  }
  std::cout << "expands=" << result.expands
            << " shrinks=" << result.shrinks << '\n';
  std::cout << "invariant=window-counts-match-state\n";
}
