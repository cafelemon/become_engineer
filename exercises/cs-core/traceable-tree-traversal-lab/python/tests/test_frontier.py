import unittest

from traceable_tree_traversal_lab import (
    BinaryTree,
    breadth_first,
    build_level_rows,
    iterative_preorder,
    recursive_preorder,
    widest_level,
)


class FrontierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = BinaryTree([7, 3, 9, None, 5, 8, 11])

    def test_iterative_matches_recursive_preorder(self) -> None:
        trace = iterative_preorder(self.tree)
        self.assertEqual(recursive_preorder(self.tree).values, trace.values)
        self.assertEqual((6, 2), (trace.visits, trace.max_frontier))

    def test_breadth_first_and_levels(self) -> None:
        trace = breadth_first(self.tree)
        self.assertEqual((7, 3, 9, 5, 8, 11), trace.values)
        self.assertEqual((6, 3), (trace.visits, trace.max_frontier))
        rows = build_level_rows(self.tree)
        self.assertEqual(((7,), (3, 9), (5, 8, 11)), tuple(row.values for row in rows))

    def test_empty_tree(self) -> None:
        tree = BinaryTree([])
        self.assertEqual(((), 0, 0), (iterative_preorder(tree).values, iterative_preorder(tree).visits, iterative_preorder(tree).max_frontier))
        self.assertEqual((), build_level_rows(tree))
        self.assertEqual((None, 0, 0), (widest_level(tree).depth, widest_level(tree).width, widest_level(tree).visits))

    def test_widest_level_prefers_earliest_tie(self) -> None:
        tree = BinaryTree([1, 2, 3])
        trace = widest_level(tree)
        self.assertEqual((1, 2, 3), (trace.depth, trace.width, trace.visits))
        single = widest_level(BinaryTree([1]))
        self.assertEqual((0, 1, 1), (single.depth, single.width, single.visits))


if __name__ == "__main__":
    unittest.main()
