#include <algorithm>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

class Trie {
 public:
  Trie() : children_(1), terminal_(1, false) {}
  void insert(const std::string& word) {
    if (word.empty()) throw std::invalid_argument("word must not be empty");
    std::size_t node = 0;
    for (char character : word) {
      if (!children_[node].contains(character)) {
        children_[node][character] = children_.size();
        children_.push_back({});
        terminal_.push_back(false);
      }
      node = children_[node][character];
    }
    terminal_[node] = true;
  }
  bool contains(const std::string& word) const {
    const auto node = walk(word);
    return node < children_.size() && terminal_[node];
  }
  std::vector<std::string> complete(const std::string& prefix) const {
    const auto node = walk(prefix);
    if (node >= children_.size()) return {};
    std::vector<std::string> results;
    const auto collect = [&](const auto& self, std::size_t current, const std::string& suffix) -> void {
      if (terminal_[current]) results.push_back(prefix + suffix);
      for (const auto& [character, next] : children_[current]) self(self, next, suffix + character);
    };
    collect(collect, node, "");
    return results;
  }
  std::size_t node_count() const { return children_.size(); }
 private:
  std::size_t walk(const std::string& text) const {
    std::size_t node = 0;
    for (char character : text) {
      const auto found = children_[node].find(character);
      if (found == children_[node].end()) return children_.size();
      node = found->second;
    }
    return node;
  }
  std::vector<std::map<char,std::size_t>> children_;
  std::vector<bool> terminal_;
};

std::vector<int> prefix_function(const std::string& pattern) {
  if (pattern.empty()) throw std::invalid_argument("pattern must not be empty");
  std::vector<int> prefix(pattern.size(), 0);
  for (std::size_t index = 1; index < pattern.size(); ++index) {
    int matched = prefix[index - 1];
    while (matched > 0 && pattern[index] != pattern[matched]) matched = prefix[matched - 1];
    if (pattern[index] == pattern[matched]) ++matched;
    prefix[index] = matched;
  }
  return prefix;
}

std::vector<int> kmp_matches(const std::string& text, const std::string& pattern) {
  const auto prefix = prefix_function(pattern);
  std::vector<int> matches;
  int matched = 0;
  for (std::size_t index = 0; index < text.size(); ++index) {
    while (matched > 0 && text[index] != pattern[matched]) matched = prefix[matched - 1];
    if (text[index] == pattern[matched]) ++matched;
    if (matched == static_cast<int>(pattern.size())) {
      matches.push_back(static_cast<int>(index + 1 - pattern.size()));
      matched = prefix[matched - 1];
    }
  }
  return matches;
}

template<class T> void print_values(const T& values) {
  bool first = true;
  for (const auto& value : values) { if (!first) std::cout << ','; first = false; std::cout << value; }
}

int main() {
  Trie trie; for (const auto& word : {"to","tea","ten","inn"}) trie.insert(word);
  const std::string pattern = "ababd";
  std::cout << "words=to,tea,ten,inn\ntrie_nodes=" << trie.node_count() << "\ncontains_te=" << (trie.contains("te")?"true":"false") << " prefix_te=";
  print_values(trie.complete("te")); std::cout << "\npattern=ababd prefix="; print_values(prefix_function(pattern));
  std::cout << "\ntext=ababcabcabababd matches="; print_values(kmp_matches("ababcabcabababd",pattern));
  std::cout << "\noverlap_aaaaa_aaa="; print_values(kmp_matches("aaaaa","aaa"));
  std::cout << "\ninvariants=shared-prefix-path,fallback-keeps-valid-border\n";
}

