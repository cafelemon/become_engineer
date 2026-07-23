"""The smallest project artifact: summarize verified study sessions."""
from __future__ import annotations


def summarize(hours: list[float]) -> dict[str, float | int]:
    if any(hour < 0 for hour in hours):
        raise ValueError("hours must be non-negative")
    return {
        "sessions": len(hours),
        "total_hours": round(sum(hours), 2),
    }


if __name__ == "__main__":
    print(summarize([1.0, 0.5, 1.25]))
