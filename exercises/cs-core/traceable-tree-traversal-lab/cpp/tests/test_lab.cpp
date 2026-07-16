#include "traceable_tree_traversal_lab/lab.hpp"

#ifdef NDEBUG
#undef NDEBUG
#endif
#include <cassert>
#include <optional>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

using namespace traceable_tree_traversal_lab;

namespace {

BinaryTree sample_tree() {
  const std::vector<std::optional<int>> slots{7, 3, 9, std::nullopt, 5, 8, 11};
  return BinaryTree(slots);
}

void test_shape_and_validation() {
  const BinaryTree empty(std::vector<std::optional<int>>{});
  const ShapeTrace empty_shape = describe_shape(empty);
  assert(empty_shape.size == 0 && empty_shape.height == -1 && empty_shape.leaf_count == 0);

  std::vector<std::optional<int>> source{7, 3, 9, std::nullopt, 5, std::nullopt};
  const BinaryTree tree(source);
  source[0] = 99;
  const ShapeTrace shape = describe_shape(tree);
  assert(shape.size == 4 && shape.height == 2 && shape.leaf_count == 2);
  assert(tree.slots().size() == 5 && tree.slot_value(0) == 7);

  bool failed = false;
  try {
    const BinaryTree invalid(std::vector<std::optional<int>>{std::nullopt});
  } catch (const std::invalid_argument&) {
    failed = true;
  }
  assert(failed);
  failed = false;
  try {
    const BinaryTree orphan(std::vector<std::optional<int>>{7, std::nullopt, 9, 4});
  } catch (const std::invalid_argument&) {
    failed = true;
  }
  assert(failed);
}

void test_slot_path() {
  const BinaryTree tree = sample_tree();
  const SlotPath path = path_to_slot(tree, 4);
  assert(path.value == 5 && path.directions == std::vector<char>({'L', 'R'}));
  assert(path_to_slot(tree, 0).directions.empty());
  bool failed = false;
  try {
    static_cast<void>(path_to_slot(tree, 3));
  } catch (const std::out_of_range&) {
    failed = true;
  }
  assert(failed);
}

void test_recursive_traversal() {
  const BinaryTree tree = sample_tree();
  assert(recursive_preorder(tree).values == std::vector<int>({7, 3, 5, 9, 8, 11}));
  assert(recursive_inorder(tree).values == std::vector<int>({3, 5, 7, 8, 9, 11}));
  assert(recursive_postorder(tree).values == std::vector<int>({5, 3, 8, 11, 9, 7}));
  assert(recursive_preorder(tree).visits == 6 && recursive_preorder(tree).max_depth == 2);
  bool failed = false;
  try {
    static_cast<void>(recursive_preorder(tree, 1));
  } catch (const std::length_error&) {
    failed = true;
  }
  assert(failed);
  assert(recursive_preorder(tree, 2).visits == 6);
}

void test_depth_count() {
  const BinaryTree tree = sample_tree();
  assert(count_at_depth(tree, 0).count == 1 && count_at_depth(tree, 0).visits == 1);
  assert(count_at_depth(tree, 1).count == 2 && count_at_depth(tree, 1).visits == 3);
  assert(count_at_depth(tree, 2).count == 3 && count_at_depth(tree, 2).visits == 6);
  assert(count_at_depth(tree, 3).count == 0 && count_at_depth(tree, 3).visits == 6);
}

void test_frontiers_and_width() {
  const BinaryTree tree = sample_tree();
  const TraversalTrace dfs = iterative_preorder(tree);
  const TraversalTrace bfs = breadth_first(tree);
  assert(dfs.values == recursive_preorder(tree).values && dfs.visits == 6 && dfs.max_frontier == 2);
  assert(bfs.values == std::vector<int>({7, 3, 9, 5, 8, 11}));
  assert(bfs.visits == 6 && bfs.max_frontier == 3);
  const std::vector<LevelRow> rows = build_level_rows(tree);
  assert(rows.size() == 3 && rows[2].values == std::vector<int>({5, 8, 11}));
  const WidthTrace width = widest_level(tree);
  assert(width.depth == 2 && width.width == 3 && width.visits == 6);

  const BinaryTree empty(std::vector<std::optional<int>>{});
  assert(iterative_preorder(empty).max_frontier == 0);
  assert(build_level_rows(empty).empty());
  assert(!widest_level(empty).depth.has_value() && widest_level(empty).width == 0);
}

void test_reports() {
  assert(build_shape_report().find("size=6，height=2，leaves=3") != std::string::npos);
  assert(build_recursive_report().find("postorder：5, 3, 8, 11, 9, 7") != std::string::npos);
  assert(build_frontier_report().find("bfs_visits=6，max_frontier=3") != std::string::npos);
}

}  // namespace

int main() {
  static_assert(!std::is_copy_constructible_v<BinaryTree>);
  static_assert(!std::is_copy_assignable_v<BinaryTree>);
  static_assert(std::is_move_constructible_v<BinaryTree>);
  static_assert(std::is_move_assignable_v<BinaryTree>);
  test_shape_and_validation();
  test_slot_path();
  test_recursive_traversal();
  test_depth_count();
  test_frontiers_and_width();
  test_reports();
}
