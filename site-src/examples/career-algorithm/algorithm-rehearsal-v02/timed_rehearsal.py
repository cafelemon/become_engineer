"""回放限时模拟的显式事件，不依赖机器墙钟生成固定快照。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EVENT_TYPES = {"start", "checkpoint", "submit", "switch"}
TERMINAL_TYPES = {"submit", "switch"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_plan(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("plan version must be 1")
    budget = payload.get("budget_minutes")
    checkpoints = payload.get("checkpoints")
    tasks = payload.get("tasks")
    if not isinstance(budget, int) or budget <= 0 or budget > 240:
        raise ValueError("budget_minutes must be an integer from 1 to 240")
    if (
        not isinstance(checkpoints, list)
        or not checkpoints
        or any(not isinstance(value, int) or value <= 0 or value >= budget for value in checkpoints)
        or checkpoints != sorted(set(checkpoints))
    ):
        raise ValueError("checkpoints must be unique increasing minutes inside budget")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list")
    ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    if len(ids) != len(tasks) or any(not isinstance(task_id, str) or not task_id for task_id in ids):
        raise ValueError("each task needs a non-empty id")
    if len(set(ids)) != len(ids):
        raise ValueError("task ids must be unique")
    priorities = [task.get("priority") for task in tasks]
    if priorities != list(range(1, len(tasks) + 1)):
        raise ValueError("task priorities must be contiguous from 1")
    return payload


def validate_events(payload: Any, plan: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("events version must be 1")
    events = payload.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("events must be a non-empty list")

    task_ids = {task["id"] for task in plan["tasks"]}
    previous_minute = -1
    active: str | None = None
    finished: set[str] = set()
    validated: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict) or set(event) != {"minute", "type", "task_id", "note"}:
            raise ValueError("each event needs minute, type, task_id and note")
        minute = event["minute"]
        event_type = event["type"]
        task_id = event["task_id"]
        note = event["note"]
        if not isinstance(minute, int) or minute < previous_minute:
            raise ValueError("event minutes must be non-decreasing integers")
        if minute > plan["budget_minutes"]:
            raise ValueError("event exceeds time budget")
        if event_type not in EVENT_TYPES or task_id not in task_ids:
            raise ValueError("event type or task id is unknown")
        if not isinstance(note, str) or not note.strip():
            raise ValueError("every event needs an evidence note")
        if event_type == "start":
            if active is not None or task_id in finished:
                raise ValueError("cannot start while another task is active or restart a finished task")
            active = task_id
        elif task_id != active:
            raise ValueError("event must target the active task")
        if event_type in TERMINAL_TYPES:
            active = None
            finished.add(task_id)
        previous_minute = minute
        validated.append(event)
    if active is not None:
        raise ValueError("active task must end with submit or switch")
    return validated


def summarize(plan: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    starts: dict[str, int] = {}
    lines = [
        f"session={plan['session_id']} budget={plan['budget_minutes']} source=declared-logical-minutes",
        f"checkpoints={','.join(str(value) for value in plan['checkpoints'])}",
    ]
    completed = 0
    switched = 0
    for event in events:
        if event["type"] == "start":
            starts[event["task_id"]] = event["minute"]
        elif event["type"] in TERMINAL_TYPES:
            duration = event["minute"] - starts[event["task_id"]]
            status = "completed" if event["type"] == "submit" else "switched"
            completed += status == "completed"
            switched += status == "switched"
            lines.append(
                f"task={event['task_id']} status={status} minutes={duration} evidence={event['note']}"
            )
    last_minute = events[-1]["minute"]
    lines.append(
        f"summary completed={completed} switched={switched} remaining={plan['budget_minutes'] - last_minute}"
    )
    lines.append("wall_clock=excluded-from-fixed-output")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default="plan.json")
    parser.add_argument("--events", default="events.json")
    args = parser.parse_args()
    try:
        plan = validate_plan(read_json(Path(args.plan)))
        events = validate_events(read_json(Path(args.events)), plan)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"rehearsal_error={error}")
        return 2
    print("\n".join(summarize(plan, events)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
