"""Layered end-to-end evaluation and fault localization for v0.35."""
from __future__ import annotations

from dataclasses import dataclass, field


LAYERS = ("task", "retrieval", "tool", "context", "trajectory", "outcome")
SENSITIVE = {"authorization", "cookie", "password", "csrf", "raw_prompt", "chain_of_thought"}


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    expected_terminal: str
    required_evidence: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    max_steps: int
    max_latency_ms: int
    max_cost_units: int


@dataclass(frozen=True)
class RunRecord:
    terminal: str
    evidence: tuple[str, ...]
    tools: tuple[str, ...]
    context_evidence: tuple[str, ...]
    steps: tuple[str, ...]
    latency_ms: int
    cost_units: int
    unsafe_action: bool = False


@dataclass
class Trace:
    run_id: str
    request_id: str
    spans: list[dict] = field(default_factory=list)

    def add(self, name: str, attributes: dict) -> None:
        clean = {key: ("[REDACTED]" if key.lower() in SENSITIVE else value) for key, value in attributes.items()}
        self.spans.append({"name": name, "attributes": clean})


def evaluate(case: EvalCase, run: RunRecord) -> dict:
    checks = {
        "task": run.terminal in {"completed", "refused", "failed", "budget_exhausted"},
        "retrieval": set(case.required_evidence) <= set(run.evidence),
        "tool": set(run.tools) <= set(case.allowed_tools) and not run.unsafe_action,
        "context": set(case.required_evidence) <= set(run.context_evidence),
        "trajectory": len(run.steps) <= case.max_steps,
        "outcome": run.terminal == case.expected_terminal,
        "latency": run.latency_ms <= case.max_latency_ms,
        "cost": run.cost_units <= case.max_cost_units,
    }
    first_failure = next((layer for layer in LAYERS if not checks[layer]), None)
    if first_failure is None:
        first_failure = next((layer for layer in ("latency", "cost") if not checks[layer]), None)
    return {"checks": checks, "passed": all(checks.values()), "first_failure": first_failure}


def aggregate(results: list[dict]) -> dict:
    total = max(1, len(results))
    return {
        "task_success_rate": sum(result["checks"]["outcome"] for result in results) / total,
        "retrieval_pass_rate": sum(result["checks"]["retrieval"] for result in results) / total,
        "tool_pass_rate": sum(result["checks"]["tool"] for result in results) / total,
        "context_pass_rate": sum(result["checks"]["context"] for result in results) / total,
        "trajectory_pass_rate": sum(result["checks"]["trajectory"] for result in results) / total,
        "gate_pass": all(result["passed"] for result in results),
    }


def fixed_report() -> str:
    case = EvalCase("acl-answer", "completed", ("acl-source",), (), 5, 800, 12)
    good = evaluate(case, RunRecord("completed", ("acl-source",), (), ("acl-source",), ("authorize", "retrieve", "answer"), 120, 4))
    missing = evaluate(case, RunRecord("refused", (), (), (), ("authorize", "retrieve"), 80, 2))
    trace = Trace("run-1", "req-1"); trace.add("answer", {"route": "rag", "authorization": "Bearer secret"})
    return "\n".join([
        f"evaluation=good:{str(good['passed']).lower()},missing-first:{missing['first_failure']}",
        "layers=task,retrieval,tool,context,trajectory,outcome,latency,cost",
        f"trace=run:run-1,request:req-1,spans:{len(trace.spans)},authorization:{trace.spans[0]['attributes']['authorization']}",
        "diagnosis=first-failing-layer:true,chain-of-thought:false",
    ])


if __name__ == "__main__": print(fixed_report())
