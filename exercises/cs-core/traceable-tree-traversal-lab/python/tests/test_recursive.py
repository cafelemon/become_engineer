import unittest

from traceable_tree_traversal_lab import (
    BinaryTree,
    TraversalDepthError,
    count_at_depth,
    recursive_inorder,
    recursive_postorder,
    recursive_preorder,
)


class RecursiveTraversalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = BinaryTree([7, 3, 9, None, 5, 8, 11])

    def test_three_orders_and_counts(self) -> None:
        self.assertEqual((7, 3, 5, 9, 8, 11), recursive_preorder(self.tree).values)
        self.assertEqual((3, 5, 7, 8, 9, 11), recursive_inorder(self.tree).values)
        self.assertEqual((5, 3, 8, 11, 9, 7), recursive_postorder(self.tree).values)
        self.assertEqual((6, 2), (recursive_preorder(self.tree).visits, recursive_preorder(self.tree).max_depth))

    def test_empty_and_single_node(self) -> None:
        self.assertEqual(((), 0, -1), (recursive_preorder(BinaryTree([])).values, recursive_preorder(BinaryTree([])).visits, recursive_preorder(BinaryTree([])).max_depth))
        self.assertEqual((7,), recursive_postorder(BinaryTree([7])).values)

    def test_explicit_depth_guard(self) -> None:
        with self.assertRaises(TraversalDepthError):
            recursive_preorder(self.tree, max_depth=1)
        with self.assertRaises(ValueError):
            recursive_preorder(self.tree, max_depth=-1)
        self.assertEqual(6, recursive_preorder(self.tree, max_depth=2).visits)

    def test_count_at_depth_prunes_deeper_nodes(self) -> None:
        self.assertEqual((1, 1), (count_at_depth(self.tree, 0).count, count_at_depth(self.tree, 0).visits))
        self.assertEqual((2, 3), (count_at_depth(self.tree, 1).count, count_at_depth(self.tree, 1).visits))
        self.assertEqual((3, 6), (count_at_depth(self.tree, 2).count, count_at_depth(self.tree, 2).visits))
        self.assertEqual((0, 6), (count_at_depth(self.tree, 3).count, count_at_depth(self.tree, 3).visits))
        with self.assertRaises(ValueError):
            count_at_depth(self.tree, -1)


if __name__ == "__main__":
    unittest.main()
