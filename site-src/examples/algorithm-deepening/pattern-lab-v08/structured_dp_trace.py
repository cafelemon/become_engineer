from __future__ import annotations

from itertools import combinations
from math import inf
from typing import Sequence


def knapsack_01(weights: Sequence[int], values: Sequence[int], capacity: int) -> tuple[int, ...]:
    if len(weights) != len(values) or capacity < 0 or any(weight <= 0 for weight in weights):
        raise ValueError("invalid knapsack input")
    dp = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for current in range(capacity, weight - 1, -1):
            dp[current] = max(dp[current], dp[current - weight] + value)
    return tuple(dp)


def knapsack_forward_wrong(weights: Sequence[int], values: Sequence[int], capacity: int) -> tuple[int, ...]:
    if len(weights) != len(values) or capacity < 0 or any(weight <= 0 for weight in weights):
        raise ValueError("invalid knapsack input")
    dp = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for current in range(weight, capacity + 1):
            dp[current] = max(dp[current], dp[current - weight] + value)
    return tuple(dp)


def knapsack_bruteforce(weights: Sequence[int], values: Sequence[int], capacity: int) -> int:
    if len(weights) != len(values) or capacity < 0:
        raise ValueError("invalid knapsack input")
    best = 0
    for size in range(len(weights) + 1):
        for chosen in combinations(range(len(weights)), size):
            if sum(weights[index] for index in chosen) <= capacity:
                best = max(best, sum(values[index] for index in chosen))
    return best


def matrix_chain(dimensions: Sequence[int]) -> tuple[int, str]:
    if len(dimensions) < 2 or any(dimension <= 0 for dimension in dimensions):
        raise ValueError("invalid matrix dimensions")
    count = len(dimensions) - 1
    cost = [[0] * count for _ in range(count)]
    split = [[0] * count for _ in range(count)]
    for length in range(2, count + 1):
        for left in range(count - length + 1):
            right = left + length - 1
            best = inf
            for middle in range(left, right):
                candidate = (
                    cost[left][middle]
                    + cost[middle + 1][right]
                    + dimensions[left] * dimensions[middle + 1] * dimensions[right + 1]
                )
                if candidate < best:
                    best = candidate
                    split[left][right] = middle
            cost[left][right] = int(best)

    def build(left: int, right: int) -> str:
        if left == right:
            return f"A{left + 1}"
        middle = split[left][right]
        return f"({build(left, middle)}{build(middle + 1, right)})"

    return cost[0][count - 1], build(0, count - 1)


def fixed_report() -> str:
    weights, values, capacity = [2, 3, 4, 5], [3, 4, 5, 8], 7
    table = knapsack_01(weights, values, capacity)
    correct_single = knapsack_01([2], [3], 4)[-1]
    wrong_single = knapsack_forward_wrong([2], [3], 4)[-1]
    matrix_cost, matrix_order = matrix_chain([10, 30, 5, 60])
    return "\n".join(
        [
            "knapsack_weights=2,3,4,5 values=3,4,5,8 capacity=7",
            f"knapsack_dp={','.join(map(str, table))}",
            f"knapsack_optimal={table[-1]}",
            f"forward_single_item={wrong_single} correct_single_item={correct_single}",
            "matrix_dims=10,30,5,60",
            f"matrix_cost={matrix_cost} order={matrix_order}",
            "orders=capacity-descending,interval-length-ascending",
            "invariants=item-used-at-most-once,subintervals-ready",
        ]
    )


if __name__ == "__main__":
    print(fixed_report())

