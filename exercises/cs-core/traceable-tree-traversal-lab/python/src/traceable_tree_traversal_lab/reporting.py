from traceable_tree_traversal_lab.traversal import (
    breadth_first,
    build_level_rows,
    iterative_preorder,
    recursive_inorder,
    recursive_postorder,
    recursive_preorder,
)
from traceable_tree_traversal_lab.tree import BinaryTree, describe_shape


def _sample_tree() -> BinaryTree:
    return BinaryTree([7, 3, 9, None, 5, 8, 11])


def _values(values: tuple[int, ...]) -> str:
    return ", ".join(str(value) for value in values)


def build_shape_report() -> str:
    tree = _sample_tree()
    shape = describe_shape(tree)
    return "\n".join(
        [
            "可追踪二叉树实验",
            "slots：7, 3, 9, null, 5, 8, 11",
            f"size={shape.size}，height={shape.height}，leaves={shape.leaf_count}",
            f"root={tree.slot_value(0)}，left={tree.slot_value(1)}，right={tree.slot_value(2)}",
        ]
    )


def build_recursive_report() -> str:
    tree = _sample_tree()
    preorder = recursive_preorder(tree)
    inorder = recursive_inorder(tree)
    postorder = recursive_postorder(tree)
    return "\n".join(
        [
            "递归深度优先遍历",
            f"preorder：{_values(preorder.values)}",
            f"inorder：{_values(inorder.values)}",
            f"postorder：{_values(postorder.values)}",
            f"visits={preorder.visits}，max_depth={preorder.max_depth}",
        ]
    )


def build_frontier_report() -> str:
    tree = _sample_tree()
    dfs = iterative_preorder(tree)
    bfs = breadth_first(tree)
    rows = build_level_rows(tree)
    levels = " ".join(f"{row.depth}=[{_values(row.values)}]" for row in rows)
    return "\n".join(
        [
            "显式前沿遍历",
            f"dfs_preorder：{_values(dfs.values)}",
            f"dfs_visits={dfs.visits}，max_frontier={dfs.max_frontier}",
            f"bfs_level_order：{_values(bfs.values)}",
            f"bfs_visits={bfs.visits}，max_frontier={bfs.max_frontier}",
            f"levels：{levels}",
        ]
    )
