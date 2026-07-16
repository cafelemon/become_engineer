from __future__ import annotations

import sys

from .reporting import build_dsu_report, build_kruskal_report, build_prim_report


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "dsu"
    reports = {"dsu": build_dsu_report, "kruskal": build_kruskal_report, "prim": build_prim_report}
    if mode not in reports or len(sys.argv) > 2:
        print(f"unknown mode: {mode}", file=sys.stderr)
        return 2
    print(reports[mode]())
    return 0


raise SystemExit(main())

