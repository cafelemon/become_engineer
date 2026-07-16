from __future__ import annotations

import sys

from .reporting import build_dijkstra_report, build_heap_report, build_queue_report


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    mode = args[0] if args else "heap"
    reports = {"heap": build_heap_report, "queue": build_queue_report, "dijkstra": build_dijkstra_report}
    if len(args) > 1 or mode not in reports:
        print(f"unknown mode: {mode}", file=sys.stderr)
        return 2
    print(reports[mode]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
