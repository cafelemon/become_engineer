import sys
from collections.abc import Sequence

from traceable_linear_structures_lab.reporting import build_linked_report, build_queue_report, build_stack_report


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) > 1:
        print("用法：python -m traceable_linear_structures_lab [linked|stack|queue]", file=sys.stderr)
        return 2
    mode = arguments[0] if arguments else "linked"
    reports = {
        "linked": build_linked_report,
        "stack": build_stack_report,
        "queue": build_queue_report,
    }
    report = reports.get(mode)
    if report is None:
        print("用法：python -m traceable_linear_structures_lab [linked|stack|queue]", file=sys.stderr)
        return 2
    print(report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
