"""示例解法：输出整数序列去重后的数量与升序结果。"""

from __future__ import annotations

import sys


def solve(raw_input: str) -> str:
    tokens = raw_input.split()
    if not tokens:
        raise ValueError("missing item count")

    count = int(tokens[0])
    if count < 0:
        raise ValueError("item count must be non-negative")

    values = [int(token) for token in tokens[1:]]
    if len(values) != count:
        raise ValueError(f"expected {count} values, got {len(values)}")

    unique = sorted(set(values))
    second_line = " ".join(str(value) for value in unique)
    return f"{len(unique)}\n{second_line}\n"


if __name__ == "__main__":
    try:
        sys.stdout.write(solve(sys.stdin.read()))
    except (TypeError, ValueError) as error:
        print(f"input_error={error}", file=sys.stderr)
        raise SystemExit(2)
