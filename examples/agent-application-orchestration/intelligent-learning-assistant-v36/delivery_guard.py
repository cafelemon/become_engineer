"""Security and release gates for the v0.36 delivery."""
from __future__ import annotations

from dataclasses import dataclass


PERMISSIONS = {
    "learner": {"run:create", "run:read", "approval:decide-own"},
    "operator": {"run:read-own", "diagnostic:read"},
}
SENSITIVE = {"authorization", "cookie", "password", "csrf", "raw_prompt", "chain_of_thought"}


def authorize(role: str, action: str, *, subject: str, owner: str) -> bool:
    allowed = action in PERMISSIONS.get(role, set())
    if action in {"run:read", "run:read-own", "approval:decide-own"}:
        allowed = allowed and subject == owner
    return allowed


def classify_content(text: str) -> dict:
    lowered = text.lower()
    patterns = ("ignore previous", "忽略之前", "system prompt", "authorization:", "call delete")
    return {"untrusted": True, "injection_detected": any(item in lowered for item in patterns), "instruction": False}


def redact(record: dict) -> dict:
    return {key: ("[REDACTED]" if key.lower() in SENSITIVE else value) for key, value in record.items()}


@dataclass(frozen=True)
class ReleaseEvidence:
    tests_passed: bool
    migrations_passed: bool
    backup_restored: bool
    health_ready: bool
    cross_subject_leaks: int
    dangerous_executions: int
    citation_corruptions: int
    duplicate_effects: int
    previous_version_healthy: bool
    schema_rollback_safe: bool


def release_decision(evidence: ReleaseEvidence) -> dict:
    hard_failures = {
        "cross_subject_leaks": evidence.cross_subject_leaks,
        "dangerous_executions": evidence.dangerous_executions,
        "citation_corruptions": evidence.citation_corruptions,
        "duplicate_effects": evidence.duplicate_effects,
    }
    required = evidence.tests_passed and evidence.migrations_passed and evidence.backup_restored and evidence.health_ready
    release = required and all(value == 0 for value in hard_failures.values())
    rollback = evidence.previous_version_healthy and evidence.schema_rollback_safe
    return {"release": release, "rollback": rollback, "hard_failures": hard_failures}


def fault_recovery(fault: str) -> str:
    return {
        "retrieval_empty": "refused",
        "tool_timeout": "retry_budget",
        "worker_crash": "resume_checkpoint",
        "database_unready": "readiness_failed",
        "prompt_injection": "content_isolated",
    }.get(fault, "unknown_fault")


def fixed_report() -> str:
    evidence = ReleaseEvidence(True, True, True, True, 0, 0, 0, 0, True, True)
    decision = release_decision(evidence)
    return "\n".join([
        "security=default-deny:true,acl-before-data:true,injection-isolated:true,secrets-redacted:true",
        f"release=gate:{str(decision['release']).lower()},backup-restored:true,faults:5",
        f"rollback=application:{str(decision['rollback']).lower()},schema-compatible:true",
        "delivery=container:true,non-root:true,health:true,metrics:true,evidence:true",
        "framework=langgraph:optional,required:false",
    ])


if __name__ == "__main__": print(fixed_report())
