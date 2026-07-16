import argparse
from collections.abc import Sequence

from traceable_array_lab.reporting import (
    build_capacity_report,
    build_grid_report,
    build_report,
    build_text_report,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m traceable_array_lab")
    parser.add_argument(
        "mode",
        nargs="?",
        default="baseline",
        choices=("baseline", "text", "grid", "capacity"),
    )
    args = parser.parse_args(argv)
    reports = {
        "baseline": build_report,
        "text": build_text_report,
        "grid": build_grid_report,
        "capacity": build_capacity_report,
    }
    print(reports[args.mode]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
