from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from safe_sales import initialize_demo_database, run_offline_tool_call


PROJECT_DIR = Path(__file__).parent
DEFAULT_DB_PATH = PROJECT_DIR / "data" / "sales.db"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a safe, read-only sales Tool Calling example."
    )
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--month", type=int, default=1)
    parser.add_argument("--product", default=None)
    parser.add_argument(
        "--use-openai",
        action="store_true",
        help="Use the optional OpenAI Responses API adapter.",
    )
    parser.add_argument(
        "--prompt",
        default="Summarize sales for January 2025.",
        help="Prompt used only with --use-openai.",
    )
    parser.add_argument("--database", type=Path, default=DEFAULT_DB_PATH)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    db_path = initialize_demo_database(args.database)

    if args.use_openai:
        from openai_adapter import run_with_openai

        try:
            print(run_with_openai(args.prompt, db_path))
        except RuntimeError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        return 0

    trace = run_offline_tool_call(
        db_path,
        year=args.year,
        month=args.month,
        product_name=args.product,
    )
    print(json.dumps(trace, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
