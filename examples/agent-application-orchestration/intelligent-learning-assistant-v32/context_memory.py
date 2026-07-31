"""Budgeted conversation context and provenance-aware memory for v0.32."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class Message:
    role: str
    text: str


@dataclass(frozen=True)
class Memory:
    memory_id: str
    owner_id: str
    kind: str
    value: str
    source: str
    consent: bool
    expires_at: datetime
    trusted_as_instruction: bool = False


@dataclass
class ContextPackage:
    messages: list[Message] = field(default_factory=list)
    summary: dict[str, object] = field(default_factory=dict)
    memories: list[Memory] = field(default_factory=list)
    knowledge: list[str] = field(default_factory=list)
    used_units: int = 0
    dropped: list[str] = field(default_factory=list)


def units(text: str) -> int:
    return max(1, len(text) // 8 + (1 if len(text) % 8 else 0))


def summarize(messages: list[Message]) -> dict[str, object]:
    user_messages = [item.text for item in messages if item.role == "user"]
    return {
        "goal": user_messages[-1][:80] if user_messages else "",
        "decisions": [],
        "open_questions": [],
        "source_message_count": len(messages),
    }


def build_context(
    subject_id: str,
    messages: list[Message],
    memories: list[Memory],
    knowledge: list[str],
    *,
    budget: int,
    now: datetime | None = None,
) -> ContextPackage:
    now = now or datetime.now(timezone.utc)
    package = ContextPackage(summary=summarize(messages))
    summary_text = str(package.summary)
    package.used_units = units(summary_text)
    if package.used_units > budget:
        package.summary = {"goal": package.summary["goal"]}
        package.used_units = units(str(package.summary))

    eligible = [
        memory for memory in memories
        if memory.owner_id == subject_id and memory.consent and memory.expires_at > now
    ]
    for memory in eligible:
        cost = units(memory.value)
        if package.used_units + cost <= budget:
            package.memories.append(memory)
            package.used_units += cost
        else:
            package.dropped.append(f"memory:{memory.memory_id}:budget")

    for item in knowledge:
        cost = units(item)
        if package.used_units + cost <= budget:
            package.knowledge.append(item)
            package.used_units += cost
        else:
            package.dropped.append("knowledge:budget")

    for message in reversed(messages):
        cost = units(message.text)
        if package.used_units + cost <= budget:
            package.messages.insert(0, message)
            package.used_units += cost
        else:
            package.dropped.append("message:window")
    return package


def memory_prompt_block(memory: Memory) -> str:
    return f"[USER_FACT source={memory.source} instruction=false] {memory.value}"


def fixed_report() -> str:
    now = datetime(2026, 7, 31, tzinfo=timezone.utc)
    memories = [Memory("m1", "alice", "preference", "喜欢分步骤解释", "user-confirmed", True, now + timedelta(days=1))]
    package = build_context("alice", [Message("user", "解释 ACL"), Message("assistant", "好的")], memories, ["ACL 在召回前执行"], budget=30, now=now)
    return "\n".join([
        f"context=summary:true,messages:{len(package.messages)},memory:{len(package.memories)},knowledge:{len(package.knowledge)}",
        f"budget=used:{package.used_units},limit:30,within:{str(package.used_units<=30).lower()}",
        "memory=owner-filtered:true,consent:true,ttl:true,instruction:false",
        "summary=structured:true,raw-chain-of-thought:false",
    ])


if __name__ == "__main__":
    print(fixed_report())
