"""Explicit workflow, router and bounded-agent boundaries for v0.31."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Mode = Literal["workflow", "router", "agent"]
Terminal = Literal["completed", "refused", "failed", "budget_exhausted"]


@dataclass(frozen=True)
class Request:
    subject_id: str
    question: str
    action: str = "answer"


@dataclass
class Run:
    mode: Mode
    request: Request
    max_steps: int = 6
    state: str = "created"
    steps: list[str] = field(default_factory=list)
    terminal: Terminal | None = None
    evidence: list[str] = field(default_factory=list)

    def transition(self, expected: str, target: str) -> None:
        if self.state != expected:
            raise ValueError(f"invalid_transition:{self.state}->{target}")
        if len(self.steps) >= self.max_steps:
            self.terminal, self.state = "budget_exhausted", "terminal"
            return
        self.steps.append(target)
        self.state = target


def choose_mode(request: Request) -> Mode:
    if request.action in {"status", "answer"}:
        return "workflow"
    if request.action in {"search", "diagnostic"}:
        return "router"
    return "agent"


def execute(request: Request, *, allowed_actions: set[str], scripted_choices: list[str] | None = None) -> Run:
    mode = choose_mode(request)
    run = Run(mode=mode, request=request)
    run.transition("created", "authorized")
    if request.action not in allowed_actions:
        run.terminal, run.state = "refused", "terminal"
        return run

    run.transition("authorized", "retrieved")
    run.evidence = ["source:v1:block-1"] if request.question.strip() else []
    if not run.evidence:
        run.terminal, run.state = "refused", "terminal"
        return run

    if mode == "workflow":
        run.transition("retrieved", "answered")
    elif mode == "router":
        run.transition("retrieved", "tool_selected")
        run.transition("tool_selected", "answered")
    else:
        choices = scripted_choices or []
        for choice in choices:
            if run.state == "terminal":
                break
            if choice == "finish":
                if run.state == "retrieved":
                    run.transition("retrieved", "answered")
                break
            if choice != "inspect":
                run.terminal, run.state = "failed", "terminal"
                return run
            expected = "retrieved" if run.state == "retrieved" else "inspected"
            run.transition(expected, "inspected")
        if run.state == "inspected":
            run.transition("inspected", "answered")
    if run.state == "answered":
        run.terminal, run.state = "completed", "terminal"
    return run


def fixed_report() -> str:
    workflow = execute(Request("alice", "ACL", "answer"), allowed_actions={"answer"})
    router = execute(Request("alice", "health", "diagnostic"), allowed_actions={"diagnostic"})
    agent = execute(Request("alice", "investigate", "open"), allowed_actions={"open"}, scripted_choices=["inspect", "finish"])
    return "\n".join([
        f"workflow=terminal:{workflow.terminal},steps:{len(workflow.steps)}",
        f"router=terminal:{router.terminal},tool-selected:{'tool_selected' in router.steps}",
        f"agent=terminal:{agent.terminal},steps:{len(agent.steps)},bounded:{len(agent.steps)<=agent.max_steps}",
        "boundary=state-schema:strict,model-transition:false,unknown-action:default-deny",
    ])


if __name__ == "__main__":
    print(fixed_report())
