#include "traceable_tree_traversal_lab/lab.hpp"

#include <algorithm>
#include <deque>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace traceable_tree_traversal_lab {

BinaryTree::BinaryTree(std::span<const std::optional<int>> values) : slots_(values.begin(), values.end()) {
  if (!slots_.empty() && !slots_.front().has_value()) {
    throw std::invalid_argument("non-empty tree requires a root value");
  }
  while (!slots_.empty() && !slots_.back().has_value()) {
    slots_.pop_back();
  }
  for (std::size_t index = 1; index < slots_.size(); ++index) {
    if (slots_[index].has_value() && !slots_[(index - 1) / 2].has_value()) {
      throw std::invalid_argument("non-empty slot has no parent");
    }
  }
  root_ = build_node(0);
}

BinaryTree::~BinaryTree() = default;
BinaryTree::BinaryTree(BinaryTree&&) noexcept = default;
BinaryTree& BinaryTree::operator=(BinaryTree&&) noexcept = default;

const std::vector<std::optional<int>>& BinaryTree::slots() const noexcept { return slots_; }

int BinaryTree::slot_value(std::size_t index) const {
  if (index >= slots_.size()) {
    throw std::out_of_range("slot index out of range");
  }
  if (!slots_[index].has_value()) {
    throw std::out_of_range("slot is empty");
  }
  return *slots_[index];
}

std::unique_ptr<BinaryTree::Node> BinaryTree::build_node(std::size_t index) const {
  if (index >= slots_.size() || !slots_[index].has_value()) {
    return nullptr;
  }
  auto node = std::make_unique<Node>(Node{*slots_[index], index, nullptr, nullptr});
  if (index <= (slots_.size() - 1) / 2) {
    node->left = build_node(index * 2 + 1);
    node->right = build_node(index * 2 + 2);
  }
  return node;
}

ShapeTrace describe_shape(const BinaryTree& tree) {
  struct Partial {
    std::size_t size;
    int height;
    std::size_t leaves;
  };
  const auto visit = [](const auto& self, const BinaryTree::Node* node) -> Partial {
    if (node == nullptr) {
      return {0, -1, 0};
    }
    const Partial left = self(self, node->left.get());
    const Partial right = self(self, node->right.get());
    const bool leaf = node->left == nullptr && node->right == nullptr;
    return {1 + left.size + right.size, 1 + std::max(left.height, right.height),
            leaf ? 1U : left.leaves + right.leaves};
  };
  const Partial result = visit(visit, tree.root_.get());
  return {result.size, result.height, result.leaves};
}

SlotPath path_to_slot(const BinaryTree& tree, std::size_t index) {
  const int value = tree.slot_value(index);
  std::vector<char> directions;
  std::size_t cursor = index;
  while (cursor > 0) {
    directions.push_back(cursor % 2 == 1 ? 'L' : 'R');
    cursor = (cursor - 1) / 2;
  }
  std::reverse(directions.begin(), directions.end());
  return {value, std::move(directions)};
}

namespace {

std::string join_values(std::span<const int> values) {
  std::ostringstream output;
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) {
      output << ", ";
    }
    output << values[index];
  }
  return output.str();
}

BinaryTree sample_tree() {
  const std::vector<std::optional<int>> slots{7, 3, 9, std::nullopt, 5, 8, 11};
  return BinaryTree(slots);
}

}  // namespace

RecursiveTrace BinaryTree::recursive_traversal(int order, std::optional<std::size_t> limit) const {
  std::vector<int> values;
  int deepest = -1;
  const auto visit = [&](const auto& self, const Node* node, std::size_t depth) -> void {
    if (node == nullptr) {
      return;
    }
    if (limit.has_value() && depth > *limit) {
      throw std::length_error("traversal depth exceeds explicit limit");
    }
    deepest = std::max(deepest, static_cast<int>(depth));
    if (order == 0) {
      values.push_back(node->value);
    }
    self(self, node->left.get(), depth + 1);
    if (order == 1) {
      values.push_back(node->value);
    }
    self(self, node->right.get(), depth + 1);
    if (order == 2) {
      values.push_back(node->value);
    }
  };
  visit(visit, root_.get(), 0);
  return {values, values.size(), deepest};
}

RecursiveTrace recursive_preorder(const BinaryTree& tree, std::optional<std::size_t> max_depth) {
  return tree.recursive_traversal(0, max_depth);
}

RecursiveTrace recursive_inorder(const BinaryTree& tree, std::optional<std::size_t> max_depth) {
  return tree.recursive_traversal(1, max_depth);
}

RecursiveTrace recursive_postorder(const BinaryTree& tree, std::optional<std::size_t> max_depth) {
  return tree.recursive_traversal(2, max_depth);
}

DepthCount count_at_depth(const BinaryTree& tree, std::size_t depth) {
  std::size_t count = 0;
  std::size_t visits = 0;
  const auto visit = [&](const auto& self, const BinaryTree::Node* node, std::size_t current) -> void {
    if (node == nullptr) {
      return;
    }
    ++visits;
    if (current == depth) {
      ++count;
      return;
    }
    self(self, node->left.get(), current + 1);
    self(self, node->right.get(), current + 1);
  };
  visit(visit, tree.root_.get(), 0);
  return {count, visits};
}

TraversalTrace iterative_preorder(const BinaryTree& tree) {
  if (tree.root_ == nullptr) {
    return {{}, 0, 0};
  }
  std::vector<const BinaryTree::Node*> frontier{tree.root_.get()};
  std::vector<int> values;
  std::size_t maximum = 1;
  while (!frontier.empty()) {
    const BinaryTree::Node* node = frontier.back();
    frontier.pop_back();
    values.push_back(node->value);
    if (node->right != nullptr) {
      frontier.push_back(node->right.get());
      maximum = std::max(maximum, frontier.size());
    }
    if (node->left != nullptr) {
      frontier.push_back(node->left.get());
      maximum = std::max(maximum, frontier.size());
    }
  }
  return {values, values.size(), maximum};
}

TraversalTrace breadth_first(const BinaryTree& tree) {
  if (tree.root_ == nullptr) {
    return {{}, 0, 0};
  }
  std::deque<const BinaryTree::Node*> frontier{tree.root_.get()};
  std::vector<int> values;
  std::size_t maximum = 1;
  while (!frontier.empty()) {
    const BinaryTree::Node* node = frontier.front();
    frontier.pop_front();
    values.push_back(node->value);
    if (node->left != nullptr) {
      frontier.push_back(node->left.get());
      maximum = std::max(maximum, frontier.size());
    }
    if (node->right != nullptr) {
      frontier.push_back(node->right.get());
      maximum = std::max(maximum, frontier.size());
    }
  }
  return {values, values.size(), maximum};
}

std::vector<LevelRow> build_level_rows(const BinaryTree& tree) {
  if (tree.root_ == nullptr) {
    return {};
  }
  std::deque<std::pair<const BinaryTree::Node*, std::size_t>> frontier{{tree.root_.get(), 0}};
  std::vector<LevelRow> rows;
  while (!frontier.empty()) {
    const auto [node, depth] = frontier.front();
    frontier.pop_front();
    if (depth == rows.size()) {
      rows.push_back({depth, {}});
    }
    rows[depth].values.push_back(node->value);
    if (node->left != nullptr) {
      frontier.emplace_back(node->left.get(), depth + 1);
    }
    if (node->right != nullptr) {
      frontier.emplace_back(node->right.get(), depth + 1);
    }
  }
  return rows;
}

WidthTrace widest_level(const BinaryTree& tree) {
  const std::vector<LevelRow> rows = build_level_rows(tree);
  if (rows.empty()) {
    return {std::nullopt, 0, 0};
  }
  std::size_t visits = 0;
  const LevelRow* widest = &rows.front();
  for (const LevelRow& row : rows) {
    visits += row.values.size();
    if (row.values.size() > widest->values.size()) {
      widest = &row;
    }
  }
  return {widest->depth, widest->values.size(), visits};
}

std::string build_shape_report() {
  const BinaryTree tree = sample_tree();
  const ShapeTrace shape = describe_shape(tree);
  std::ostringstream output;
  output << "可追踪二叉树实验\n"
         << "slots：7, 3, 9, null, 5, 8, 11\n"
         << "size=" << shape.size << "，height=" << shape.height << "，leaves=" << shape.leaf_count << '\n'
         << "root=" << tree.slot_value(0) << "，left=" << tree.slot_value(1) << "，right=" << tree.slot_value(2);
  return output.str();
}

std::string build_recursive_report() {
  const BinaryTree tree = sample_tree();
  const RecursiveTrace preorder = recursive_preorder(tree);
  const RecursiveTrace inorder = recursive_inorder(tree);
  const RecursiveTrace postorder = recursive_postorder(tree);
  std::ostringstream output;
  output << "递归深度优先遍历\n"
         << "preorder：" << join_values(preorder.values) << '\n'
         << "inorder：" << join_values(inorder.values) << '\n'
         << "postorder：" << join_values(postorder.values) << '\n'
         << "visits=" << preorder.visits << "，max_depth=" << preorder.max_depth;
  return output.str();
}

std::string build_frontier_report() {
  const BinaryTree tree = sample_tree();
  const TraversalTrace dfs = iterative_preorder(tree);
  const TraversalTrace bfs = breadth_first(tree);
  const std::vector<LevelRow> rows = build_level_rows(tree);
  std::ostringstream levels;
  for (std::size_t index = 0; index < rows.size(); ++index) {
    if (index > 0) {
      levels << ' ';
    }
    levels << rows[index].depth << "=[" << join_values(rows[index].values) << ']';
  }
  std::ostringstream output;
  output << "显式前沿遍历\n"
         << "dfs_preorder：" << join_values(dfs.values) << '\n'
         << "dfs_visits=" << dfs.visits << "，max_frontier=" << dfs.max_frontier << '\n'
         << "bfs_level_order：" << join_values(bfs.values) << '\n'
         << "bfs_visits=" << bfs.visits << "，max_frontier=" << bfs.max_frontier << '\n'
         << "levels：" << levels.str();
  return output.str();
}

}  // namespace traceable_tree_traversal_lab
