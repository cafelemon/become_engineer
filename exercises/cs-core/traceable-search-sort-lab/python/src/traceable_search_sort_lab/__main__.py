import sys
from collections.abc import Callable, Sequence

from traceable_search_sort_lab.reporting import (
    build_elementary_report,
    build_merge_report,
    build_search_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    usage = "用法：python -m traceable_search_sort_lab [search|elementary|merge]"
    if len(arguments) > 1:
        print(usage, file=sys.stderr)
        return 2
    mode = arguments[0] if arguments else "search"
    reports: dict[str, Callable[[], str]] = {
        "search": build_search_report,
        "elementary": build_elementary_report,
        "merge": build_merge_report,
    }
    report = reports.get(mode)
    if report is None:
        print(usage, file=sys.stderr)
        return 2
    print(report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
