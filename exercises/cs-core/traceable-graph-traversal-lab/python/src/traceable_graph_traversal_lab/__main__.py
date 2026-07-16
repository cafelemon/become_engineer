from __future__ import annotations

import sys
from collections.abc import Sequence

from .reporting import build_bfs_report, build_dfs_report, build_graph_report


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    mode = arguments[0] if arguments else "graph"
    reports = {"graph": build_graph_report, "bfs": build_bfs_report, "dfs": build_dfs_report}
    if len(arguments) > 1 or mode not in reports:
        print(f"unknown mode: {mode}", file=sys.stderr)
        return 2
    print(reports[mode]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
