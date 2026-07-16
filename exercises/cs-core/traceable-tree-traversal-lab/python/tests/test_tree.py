import unittest

from traceable_tree_traversal_lab import BinaryTree, describe_shape, path_to_slot


class TreeTests(unittest.TestCase):
    def test_empty_and_leaf_shape(self) -> None:
        empty = describe_shape(BinaryTree([]))
        leaf = describe_shape(BinaryTree([7]))
        self.assertEqual((0, -1, 0), (empty.size, empty.height, empty.leaf_count))
        self.assertEqual((1, 0, 1), (leaf.size, leaf.height, leaf.leaf_count))

    def test_sparse_shape_and_normalization(self) -> None:
        source: list[int | None] = [7, 3, 9, None, 5, None, None, None]
        tree = BinaryTree(source)
        source[0] = 99
        self.assertEqual((7, 3, 9, None, 5), tree.slots)
        self.assertEqual((4, 2, 2), (describe_shape(tree).size, describe_shape(tree).height, describe_shape(tree).leaf_count))

    def test_negative_and_duplicate_values_are_valid(self) -> None:
        tree = BinaryTree([-1, -1, 2])
        self.assertEqual((-1, -1, 2), tree.slots)

    def test_invalid_root_and_orphan_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BinaryTree([None])
        with self.assertRaises(ValueError):
            BinaryTree([7, None, 9, 4])

    def test_checked_slot_and_path(self) -> None:
        tree = BinaryTree([7, 3, 9, None, 5])
        self.assertEqual((5, ("L", "R")), (path_to_slot(tree, 4).value, path_to_slot(tree, 4).directions))
        self.assertEqual((), path_to_slot(tree, 0).directions)
        for index in (-1, 3, 8):
            with self.assertRaises(IndexError):
                path_to_slot(tree, index)


if __name__ == "__main__":
    unittest.main()
