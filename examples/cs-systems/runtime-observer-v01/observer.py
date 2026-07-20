from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys


WORKER = Path(__file__).with_name("worker.py")


@dataclass(frozen=True)
class RunResult:
    mode: str
    parent_pid: int
    child_pid: int | None
    reported_parent_pid: int | None
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool


def run_worker(mode: str, timeout: float = 0.3) -> RunResult:
    command = [sys.executable, str(WORKER), "--mode", mode]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        return RunResult(
            mode=mode,
            parent_pid=os.getpid(),
            child_pid=None,
            reported_parent_pid=None,
            returncode=None,
            stdout=(error.stdout or "").strip(),
            stderr=(error.stderr or "").strip(),
            timed_out=True,
        )

    payload = json.loads(completed.stdout)
    return RunResult(
        mode=mode,
        parent_pid=os.getpid(),
        child_pid=int(payload["pid"]),
        reported_parent_pid=int(payload["parent_pid"]),
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
        timed_out=False,
    )


def main() -> None:
    success = run_worker("success")
    failure = run_worker("fail")
    timeout = run_worker("sleep", timeout=0.05)
    print(
        "success: "
        f"exit={success.returncode} "
        f"child_different={success.child_pid != success.parent_pid} "
        f"parent_matches={success.reported_parent_pid == success.parent_pid}"
    )
    print(f"failure: exit={failure.returncode} stderr={failure.stderr}")
    print(f"timeout: timed_out={timeout.timed_out}")


if __name__ == "__main__":
    main()
