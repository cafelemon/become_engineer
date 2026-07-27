from __future__ import annotations

from itertools import combinations
from typing import Sequence


def best_non_adjacent(values: Sequence[int]) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    dp = [0] * (len(values) + 1)
    for prefix in range(1, len(values) + 1):
        skip = dp[prefix - 1]
        take = values[prefix - 1] + (dp[prefix - 2] if prefix >= 2 else 0)
        dp[prefix] = max(skip, take)

    chosen: list[int] = []
    prefix = len(values)
    while prefix > 0:
        skip = dp[prefix - 1]
        take = values[prefix - 1] + (dp[prefix - 2] if prefix >= 2 else 0)
        if take > skip:
            chosen.append(prefix - 1)
            prefix -= 2
        else:
            prefix -= 1
    chosen.reverse()
    return dp[-1], tuple(chosen), tuple(dp)


def best_non_adjacent_bruteforce(values: Sequence[int]) -> int:
    best = 0
    indices = range(len(values))
    for size in range(len(values) + 1):
        for chosen in combinations(indices, size):
            if all(chosen[index] - chosen[index - 1] > 1 for index in range(1, len(chosen))):
                best = max(best, sum(values[index] for index in chosen))
    return best


def highest_first(values: Sequence[int]) -> tuple[int, tuple[int, ...]]:
    blocked: set[int] = set()
    chosen: list[int] = []
    for index in sorted(range(len(values)), key=lambda item: (-values[item], item)):
        if values[index] <= 0 or index in blocked:
            continue
        chosen.append(index)
        blocked.update((index - 1, index, index + 1))
    chosen.sort()
    return sum(values[index] for index in chosen), tuple(chosen)


def fixed_report() -> str:
    values = [4, 5, 4, 1, 1]
    total, chosen, dp = best_non_adjacent(values)
    greedy_total, greedy_chosen = highest_first(values)
    return "\n".join(
        [
            "values=4,5,4,1,1",
            f"dp={','.join(map(str, dp))}",
            f"optimal={total} chosen_indices={','.join(map(str, chosen))}",
            f"highest_first={greedy_total} chosen_indices={','.join(map(str, greedy_chosen))}",
            "transition=dp[i]=max(dp[i-1],dp[i-2]+value[i-1])",
            "tie=skip-current",
            "invariant=dp-prefix-optimum",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())
