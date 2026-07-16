#pragma once

#include <cstddef>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace traceable_tree_traversal_lab {

struct ShapeTrace {
  std::size_t size;
  int height;
  std::size_t leaf_count;
};

struct SlotPath {
  int value;
  std::vector<char> directions;
};

struct RecursiveTrace {
  std::vector<int> values;
  std::size_t visits;
  int max_depth;
};

struct DepthCount {
  std::size_t count;
  std::size_t visits;
};

struct TraversalTrace {
  std::vector<int> values;
  std::size_t visits;
  std::size_t max_frontier;
};

struct LevelRow {
  std::size_t depth;
  std::vector<int> values;
};

struct WidthTrace {
  std::optional<std::size_t> depth;
  std::size_t width;
  std::size_t visits;
};

class BinaryTree;
[[nodiscard]] ShapeTrace describe_shape(const BinaryTree& tree);
[[nodiscard]] SlotPath path_to_slot(const BinaryTree& tree, std::size_t index);
[[nodiscard]] RecursiveTrace recursive_preorder(const BinaryTree& tree,
                                                 std::optional<std::size_t> max_depth = std::nullopt);
[[nodiscard]] RecursiveTrace recursive_inorder(const BinaryTree& tree,
                                                std::optional<std::size_t> max_depth = std::nullopt);
[[nodiscard]] RecursiveTrace recursive_postorder(const BinaryTree& tree,
                                                  std::optional<std::size_t> max_depth = std::nullopt);
[[nodiscard]] DepthCount count_at_depth(const BinaryTree& tree, std::size_t depth);
[[nodiscard]] TraversalTrace iterative_preorder(const BinaryTree& tree);
[[nodiscard]] TraversalTrace breadth_first(const BinaryTree& tree);
[[nodiscard]] std::vector<LevelRow> build_level_rows(const BinaryTree& tree);
[[nodiscard]] WidthTrace widest_level(const BinaryTree& tree);

class BinaryTree {
 public:
  explicit BinaryTree(std::span<const std::optional<int>> values);
  ~BinaryTree();
  BinaryTree(BinaryTree&&) noexcept;
  BinaryTree& operator=(BinaryTree&&) noexcept;
  BinaryTree(const BinaryTree&) = delete;
  BinaryTree& operator=(const BinaryTree&) = delete;

  [[nodiscard]] const std::vector<std::optional<int>>& slots() const noexcept;
  [[nodiscard]] int slot_value(std::size_t index) const;

 private:
  struct Node {
    int value;
    std::size_t slot_index;
    std::unique_ptr<Node> left;
    std::unique_ptr<Node> right;
  };

  [[nodiscard]] std::unique_ptr<Node> build_node(std::size_t index) const;
  [[nodiscard]] RecursiveTrace recursive_traversal(int order,
                                                   std::optional<std::size_t> max_depth) const;

  std::vector<std::optional<int>> slots_;
  std::unique_ptr<Node> root_;

  friend ShapeTrace describe_shape(const BinaryTree& tree);
  friend RecursiveTrace recursive_preorder(const BinaryTree& tree, std::optional<std::size_t> max_depth);
  friend RecursiveTrace recursive_inorder(const BinaryTree& tree, std::optional<std::size_t> max_depth);
  friend RecursiveTrace recursive_postorder(const BinaryTree& tree, std::optional<std::size_t> max_depth);
  friend DepthCount count_at_depth(const BinaryTree& tree, std::size_t depth);
  friend TraversalTrace iterative_preorder(const BinaryTree& tree);
  friend TraversalTrace breadth_first(const BinaryTree& tree);
  friend std::vector<LevelRow> build_level_rows(const BinaryTree& tree);
};

[[nodiscard]] std::string build_shape_report();
[[nodiscard]] std::string build_recursive_report();
[[nodiscard]] std::string build_frontier_report();

}  // namespace traceable_tree_traversal_lab
