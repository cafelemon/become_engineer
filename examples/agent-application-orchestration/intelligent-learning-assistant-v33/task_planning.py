"""Strict task plans, dependency checks and bounded replanning for v0.33."""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Task:
    task_id: str
    action: str
    depends_on: tuple[str, ...] = ()
    budget: int = 1
    status: str = "pending"
    attempts: int = 0


@dataclass(frozen=True)
class Plan:
    goal: str
    tasks: tuple[Task, ...]
    max_tasks: int = 6
    total_budget: int = 12
    revision: int = 1


ALLOWED_ACTIONS = {"retrieve", "summarize", "compare", "draft", "request_approval"}
RETRYABLE_FAILURES = {"timeout", "temporary_unavailable", "lease_lost"}


def validate(plan: Plan) -> None:
    if not 1 <= len(plan.tasks) <= plan.max_tasks:
        raise ValueError("task_count")
    if sum(task.budget for task in plan.tasks) > plan.total_budget:
        raise ValueError("total_budget")
    ids = [task.task_id for task in plan.tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_task")
    for task in plan.tasks:
        if task.action not in ALLOWED_ACTIONS or task.budget < 1:
            raise ValueError("invalid_task")
        if any(dep not in ids for dep in task.depends_on):
            raise ValueError("unknown_dependency")
    visiting: set[str] = set()
    visited: set[str] = set()
    graph = {task.task_id: task.depends_on for task in plan.tasks}

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError("dependency_cycle")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in graph[task_id]:
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)


def ready_tasks(plan: Plan) -> tuple[Task, ...]:
    complete = {task.task_id for task in plan.tasks if task.status == "completed"}
    return tuple(task for task in plan.tasks if task.status == "pending" and set(task.depends_on) <= complete)


def classify_failure(code: str) -> str:
    return "retryable" if code in RETRYABLE_FAILURES else "terminal"


def apply_result(plan: Plan, task_id: str, *, success: bool, failure_code: str = "") -> Plan:
    updated = []
    for task in plan.tasks:
        if task.task_id != task_id:
            updated.append(task)
            continue
        attempts = task.attempts + 1
        if success:
            updated.append(replace(task, status="completed", attempts=attempts))
        elif classify_failure(failure_code) == "retryable" and attempts < task.budget:
            updated.append(replace(task, status="pending", attempts=attempts))
        else:
            updated.append(replace(task, status="failed", attempts=attempts))
    result = replace(plan, tasks=tuple(updated))
    validate(result)
    return result


def replan(plan: Plan, replacements: tuple[Task, ...]) -> Plan:
    completed = tuple(task for task in plan.tasks if task.status == "completed")
    completed_ids = {task.task_id for task in completed}
    if any(task.task_id in completed_ids for task in replacements):
        raise ValueError("completed_task_immutable")
    result = Plan(plan.goal, completed + replacements, plan.max_tasks, plan.total_budget, plan.revision + 1)
    validate(result)
    return result


def terminal(plan: Plan) -> str | None:
    if any(task.status == "failed" for task in plan.tasks):
        return "failed"
    if all(task.status == "completed" for task in plan.tasks):
        return "completed"
    if not ready_tasks(plan):
        return "blocked"
    return None


def fixed_report() -> str:
    plan = Plan("比较两份资料", (Task("retrieve-a", "retrieve"), Task("retrieve-b", "retrieve"), Task("compare", "compare", ("retrieve-a", "retrieve-b"), 2)))
    validate(plan)
    plan = apply_result(plan, "retrieve-a", success=True)
    return "\n".join([
        f"plan=revision:{plan.revision},tasks:{len(plan.tasks)},budget:{sum(t.budget for t in plan.tasks)}/{plan.total_budget}",
        f"ready={','.join(task.task_id for task in ready_tasks(plan))}",
        "failure=timeout:retryable,permission_denied:terminal",
        "replan=completed-immutable:true,max-tasks:6,termination:explicit",
    ])


if __name__ == "__main__":
    print(fixed_report())
