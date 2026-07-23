"""验证错因、反例候选和回归证据是否形成闭环。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CATEGORIES = {"contract", "boundary", "implementation", "complexity", "strategy"}
OBSERVED_STATUSES = {"wrong-answer", "runtime-error", "timeout", "switched"}
REQUIRED_KEYS = {
    "id",
    "observed_status",
    "category",
    "counterexample",
    "smaller_probe",
    "cause",
    "fix",
    "regression_id",
    "after",
    "linked_event",
}


def load_records(path: Path) -> list[dict[str, str]]:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("failure file version must be 1")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")

    ids: set[str] = set()
    regressions: set[str] = set()
    validated: list[dict[str, str]] = []
    for record in records:
        if not isinstance(record, dict) or set(record) != REQUIRED_KEYS:
            raise ValueError("each record must use the exact failure evidence schema")
        if any(not isinstance(record[key], str) or not record[key].strip() for key in REQUIRED_KEYS):
            raise ValueError("failure evidence fields must be non-empty strings")
        if record["id"] in ids or record["regression_id"] in regressions:
            raise ValueError("record ids and regression ids must be unique")
        if record["category"] not in CATEGORIES:
            raise ValueError("unknown failure category")
        if record["observed_status"] not in OBSERVED_STATUSES:
            raise ValueError("unknown observed status")
        if record["after"] != "regression-pass":
            raise ValueError("every record must end in regression-pass")
        if ":" not in record["linked_event"]:
            raise ValueError("linked_event must identify a timeline event")
        ids.add(record["id"])
        regressions.add(record["regression_id"])
        validated.append(record)
    return validated


def build_report(records: list[dict[str, str]]) -> list[str]:
    lines = [
        (
            f"failure={record['id']} category={record['category']} "
            f"before={record['observed_status']} after={record['after']} "
            f"regression={record['regression_id']}"
        )
        for record in records
    ]
    categories = sorted({record["category"] for record in records})
    lines.append(f"coverage categories={','.join(categories)}")
    lines.append(f"gate=pass records={len(records)}")
    lines.append("claim=counterexample-candidate-not-proof-of-global-minimality")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--failures", default="failures.json")
    args = parser.parse_args()
    try:
        records = load_records(Path(args.failures))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"retrospective_error={error}")
        return 2
    print("\n".join(build_report(records)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
