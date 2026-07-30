"""Deterministic, subject-scoped memory and context assembly."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BANNED_FIELDS = {"prompt", "reasoning", "chain_of_thought"}


class MemoryError(ValueError):
    """A memory record or context request violates the public contract."""


@dataclass(frozen=True)
class ContextEntry:
    entry_id: str
    category: str
    content: str
    source_id: str


@dataclass(frozen=True)
class ContextBundle:
    entries: tuple[ContextEntry, ...]
    used_chars: int
    budget_chars: int


class MemoryStore:
    def __init__(self, database: str | Path) -> None:
        self.connection = sqlite3.connect(str(database))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_facts(
                memory_id TEXT PRIMARY KEY,
                subject_id TEXT NOT NULL,
                content TEXT NOT NULL,
                source_id TEXT NOT NULL,
                consent INTEGER NOT NULL CHECK(consent IN (0, 1)),
                expires_at INTEGER NOT NULL,
                priority INTEGER NOT NULL CHECK(priority BETWEEN 0 AND 9)
            )
            """
        )

    def close(self) -> None:
        self.connection.close()

    def add_fact(
        self,
        *,
        memory_id: str,
        subject_id: str,
        content: str,
        source_id: str,
        consent: bool,
        expires_at: int,
        priority: int = 5,
    ) -> None:
        values = (memory_id, subject_id, content, source_id)
        if any(not value.strip() for value in values):
            raise MemoryError("memory_id, subject_id, content and source_id are required")
        if not 0 <= priority <= 9:
            raise MemoryError("priority must be between 0 and 9")
        self.connection.execute(
            """
            INSERT INTO memory_facts(
                memory_id, subject_id, content, source_id,
                consent, expires_at, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                subject_id,
                content,
                source_id,
                int(consent),
                expires_at,
                priority,
            ),
        )
        self.connection.commit()

    def eligible_facts(self, *, subject_id: str, now: int) -> tuple[sqlite3.Row, ...]:
        return tuple(
            self.connection.execute(
                """
                SELECT memory_id, content, source_id, priority
                FROM memory_facts
                WHERE subject_id = ?
                  AND consent = 1
                  AND expires_at > ?
                ORDER BY priority DESC, memory_id ASC
                """,
                (subject_id, now),
            )
        )

    def count(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM memory_facts").fetchone()[0])


class ContextAssembler:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def assemble(
        self,
        *,
        subject_id: str,
        now: int,
        working_memory: Iterable[dict[str, str]],
        budget_chars: int,
    ) -> ContextBundle:
        if not subject_id.strip():
            raise MemoryError("subject_id is required")
        if budget_chars <= 0:
            raise MemoryError("budget_chars must be positive")

        candidates: list[ContextEntry] = []
        for index, item in enumerate(working_memory):
            if BANNED_FIELDS.intersection(item):
                raise MemoryError("hidden prompt or reasoning fields are forbidden")
            if set(item) != {"content", "source_id"}:
                raise MemoryError("working memory fields must be content and source_id")
            if not item["content"].strip() or not item["source_id"].strip():
                raise MemoryError("working memory content and source are required")
            candidates.append(
                ContextEntry(
                    entry_id=f"working-{index + 1}",
                    category="working",
                    content=item["content"],
                    source_id=item["source_id"],
                )
            )

        for row in self.store.eligible_facts(subject_id=subject_id, now=now):
            candidates.append(
                ContextEntry(
                    entry_id=row["memory_id"],
                    category="fact",
                    content=row["content"],
                    source_id=row["source_id"],
                )
            )

        selected: list[ContextEntry] = []
        used = 0
        for candidate in candidates:
            size = len(candidate.content)
            if used + size <= budget_chars:
                selected.append(candidate)
                used += size
        return ContextBundle(tuple(selected), used, budget_chars)


def fixed_report() -> str:
    store = MemoryStore(":memory:")
    try:
        store.add_fact(
            memory_id="fact-preference",
            subject_id="learner-a",
            content="prefers examples",
            source_id="profile-form",
            consent=True,
            expires_at=200,
            priority=8,
        )
        store.add_fact(
            memory_id="fact-unconsented",
            subject_id="learner-a",
            content="private note",
            source_id="profile-form",
            consent=False,
            expires_at=200,
            priority=9,
        )
        store.add_fact(
            memory_id="fact-expired",
            subject_id="learner-a",
            content="old preference",
            source_id="profile-form",
            consent=True,
            expires_at=90,
            priority=9,
        )
        store.add_fact(
            memory_id="fact-other-subject",
            subject_id="learner-b",
            content="other learner",
            source_id="profile-form",
            consent=True,
            expires_at=200,
            priority=9,
        )
        bundle = ContextAssembler(store).assemble(
            subject_id="learner-a",
            now=100,
            working_memory=[{"content": "review arrays", "source_id": "run-20"}],
            budget_chars=29,
        )
        entries = ",".join(f"{entry.category}:{entry.entry_id}" for entry in bundle.entries)
        return "\n".join(
            [
                "runtime=python:3.11+,dependencies:stdlib-only,storage:sqlite,network:disabled",
                "memory=working:ephemeral,facts:persistent,source-required:true,consent-filter:true,ttl-filter:true,subject-isolation:true",
                f"stored={store.count()},eligible=1,assembled={entries}",
                f"budget=used-chars:{bundle.used_chars},limit-chars:{bundle.budget_chars},deterministic:true",
                "excluded=unconsented:true,expired:true,other-subject:true,hidden-reasoning:true",
                "invariants=explicit-memory-only,source-bound,consent-before-use,ttl-enforced,subject-scoped,budget-bounded,no-hidden-chain-of-thought,no-network",
            ]
        )
    finally:
        store.close()


if __name__ == "__main__":
    print(fixed_report())
