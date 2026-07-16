import sys

from traceable_tree_traversal_lab.reporting import (
    build_frontier_report,
    build_recursive_report,
    build_shape_report,
)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "shape"
    if len(sys.argv) > 2 or mode not in {"shape", "recursive", "frontier"}:
        print(f"unknown mode: {mode}", file=sys.stderr)
        return 2
    builders = {
        "shape": build_shape_report,
        "recursive": build_recursive_report,
        "frontier": build_frontier_report,
    }
    print(builders[mode]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
