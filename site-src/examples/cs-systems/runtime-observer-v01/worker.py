from __future__ import annotations

import argparse
import json
import os
import sys
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("success", "fail", "sleep"), required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode == "sleep":
        time.sleep(2)
        return 0

    print(json.dumps({"pid": os.getpid(), "parent_pid": os.getppid(), "mode": args.mode}))
    if args.mode == "fail":
        print("simulated worker failure", file=sys.stderr)
        return 7
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
