import sys
from collections.abc import Sequence

from traceable_hash_lab.reporting import build_applications_report, build_hash_report, build_table_report


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) > 1:
        print("用法：python -m traceable_hash_lab [hash|table|applications]", file=sys.stderr)
        return 2
    mode = arguments[0] if arguments else "hash"
    reports = {
        "hash": build_hash_report,
        "table": build_table_report,
        "applications": build_applications_report,
    }
    report = reports.get(mode)
    if report is None:
        print("用法：python -m traceable_hash_lab [hash|table|applications]", file=sys.stderr)
        return 2
    print(report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
