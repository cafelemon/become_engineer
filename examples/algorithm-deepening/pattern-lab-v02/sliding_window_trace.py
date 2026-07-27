from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class BestWindow:
    left: int
    right: int
    text: str


@dataclass(frozen=True)
class WindowResult:
    best: BestWindow | None
    improvements: tuple[BestWindow, ...]
    expands: int
    shrinks: int


def minimum_cover(text: str, need: str) -> WindowResult:
    if not need:
        raise ValueError("need must not be empty")
    required = Counter(need)
    current: Counter[str] = Counter()
    formed = 0
    left = 0
    shrinks = 0
    best: BestWindow | None = None
    improvements: list[BestWindow] = []

    for right, character in enumerate(text):
        current[character] += 1
        if character in required and current[character] == required[character]:
            formed += 1

        while formed == len(required):
            candidate = BestWindow(left, right, text[left : right + 1])
            if best is None or len(candidate.text) < len(best.text):
                best = candidate
                improvements.append(candidate)

            removed = text[left]
            current[removed] -= 1
            left += 1
            shrinks += 1
            if removed in required and current[removed] < required[removed]:
                formed -= 1

    return WindowResult(best, tuple(improvements), len(text), shrinks)


def fixed_report() -> str:
    result = minimum_cover("ADOBECODEBANC", "ABC")
    lines = [
        "input=ADOBECODEBANC need=ABC",
        "required_kinds=3",
    ]
    lines.extend(
        f"best={item.left}:{item.right} text={item.text}"
        for item in result.improvements
    )
    if result.best is None:
        lines.append("result=not-found")
    else:
        lines.append(
            f"result={result.best.left}:{result.best.right} text={result.best.text}"
        )
    lines.append(f"expands={result.expands} shrinks={result.shrinks}")
    lines.append("invariant=window-counts-match-state")
    return "\n".join(lines)


if __name__ == "__main__":
    print(fixed_report())
