"""本机确定性判题器：真实子进程、固定输入输出、无外网依赖。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ALLOWED_CASE_KEYS = {"id", "input", "expected"}


def normalize_output(value: str) -> str:
    """统一换行和行尾空白；保留行内空格差异。"""
    lines = value.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    while lines and not lines[-1].rstrip():
        lines.pop()
    return "\n".join(line.rstrip() for line in lines) + "\n"


def resolve_local_file(workspace: Path, candidate: str, label: str) -> Path:
    if not candidate or Path(candidate).is_absolute():
        raise ValueError(f"{label} must be a relative path")
    root = workspace.resolve()
    path = (root / candidate).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"{label} escapes workspace")
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {candidate}")
    return path


def load_cases(path: Path) -> list[dict[str, str]]:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("case file version must be 1")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")

    seen: set[str] = set()
    validated: list[dict[str, str]] = []
    for case in cases:
        if not isinstance(case, dict) or set(case) != ALLOWED_CASE_KEYS:
            raise ValueError("each case must contain only id, input and expected")
        if not all(isinstance(case[key], str) for key in ALLOWED_CASE_KEYS):
            raise ValueError("case id, input and expected must be strings")
        if not case["id"] or case["id"] in seen:
            raise ValueError("case ids must be non-empty and unique")
        seen.add(case["id"])
        validated.append(case)
    return validated


def run_case(solution: Path, case: dict[str, str], timeout_seconds: float) -> tuple[str, str]:
    try:
        completed = subprocess.run(
            [sys.executable, str(solution)],
            input=case["input"],
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "timeout", "time-limit-exceeded"

    if completed.returncode != 0:
        return "runtime-error", f"exit-{completed.returncode}"
    if normalize_output(completed.stdout) != normalize_output(case["expected"]):
        return "wrong-answer", "stdout-mismatch"
    return "pass", "output-matched"


def run_suite(
    workspace: Path,
    solution_name: str,
    cases_name: str,
    timeout_seconds: float,
) -> tuple[list[str], int]:
    if timeout_seconds <= 0 or timeout_seconds > 10:
        raise ValueError("timeout must be greater than 0 and at most 10 seconds")
    solution = resolve_local_file(workspace, solution_name, "solution")
    cases_path = resolve_local_file(workspace, cases_name, "cases")
    cases = load_cases(cases_path)

    lines: list[str] = []
    passed = 0
    for case in cases:
        status, reason = run_case(solution, case, timeout_seconds)
        passed += status == "pass"
        lines.append(f"case={case['id']} status={status} reason={reason}")
    lines.append(f"summary passed={passed} total={len(cases)}")
    lines.append("timing=excluded-from-fixed-output")
    return lines, 0 if passed == len(cases) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--solution", default="solution.py")
    parser.add_argument("--cases", default="cases.json")
    parser.add_argument("--timeout", type=float, default=1.0)
    args = parser.parse_args()

    try:
        lines, exit_code = run_suite(
            Path(args.workspace),
            args.solution,
            args.cases,
            args.timeout,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"judge_error={error}")
        return 2
    print("\n".join(lines))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
