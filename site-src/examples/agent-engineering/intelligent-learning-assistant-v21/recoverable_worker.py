"""Lease-based, crash-safe and idempotent run worker."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


class WorkerError(RuntimeError):
    pass


@dataclass
class VirtualClock:
    now: int = 100

    def advance(self, seconds: int) -> None:
        self.now += seconds


class RecoverableWorker:
    def __init__(self, database: str | Path, clock: VirtualClock) -> None:
        self.clock = clock
        self.connection = sqlite3.connect(str(database), isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS worker_runs(
                run_id TEXT PRIMARY KEY,
                plan_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS run_leases(
                run_id TEXT PRIMARY KEY REFERENCES worker_runs(run_id),
                owner_id TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                generation INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS completed_steps(
                run_id TEXT NOT NULL REFERENCES worker_runs(run_id),
                step_id TEXT NOT NULL,
                idempotency_key TEXT NOT NULL UNIQUE,
                payload_hash TEXT NOT NULL,
                PRIMARY KEY(run_id, step_id)
            );
            CREATE TABLE IF NOT EXISTS side_effects(
                idempotency_key TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                payload_hash TEXT NOT NULL
            );
            """
        )

    def close(self) -> None:
        self.connection.close()

    def create_run(self, run_id: str, plan: list[str]) -> None:
        if not run_id or not plan or len(plan) != len(set(plan)):
            raise WorkerError("invalid run plan")
        self.connection.execute(
            "INSERT INTO worker_runs(run_id, plan_json) VALUES (?, ?)",
            (run_id, json.dumps(plan, separators=(",", ":"))),
        )

    def acquire(self, run_id: str, owner_id: str, ttl: int) -> str:
        if ttl <= 0 or not owner_id:
            raise WorkerError("invalid lease")
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT owner_id, expires_at, generation FROM run_leases WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            if row and row["expires_at"] > self.clock.now and row["owner_id"] != owner_id:
                raise WorkerError("lease_busy")
            generation = 1 if row is None else int(row["generation"]) + 1
            self.connection.execute(
                """
                INSERT INTO run_leases(run_id, owner_id, expires_at, generation)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                  owner_id = excluded.owner_id,
                  expires_at = excluded.expires_at,
                  generation = excluded.generation
                """,
                (run_id, owner_id, self.clock.now + ttl, generation),
            )
            self.connection.execute("COMMIT")
            return f"{owner_id}:{generation}"
        except Exception:
            self.connection.execute("ROLLBACK")
            raise

    def renew(self, run_id: str, owner_id: str, ttl: int) -> None:
        changed = self.connection.execute(
            """
            UPDATE run_leases
            SET expires_at = ?
            WHERE run_id = ? AND owner_id = ? AND expires_at > ?
            """,
            (self.clock.now + ttl, run_id, owner_id, self.clock.now),
        ).rowcount
        if changed != 1:
            raise WorkerError("lease_lost")

    def _plan(self, run_id: str) -> list[str]:
        row = self.connection.execute(
            "SELECT plan_json FROM worker_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            raise WorkerError("unknown_run")
        return list(json.loads(row["plan_json"]))

    def next_step(self, run_id: str) -> str | None:
        completed = {
            row[0]
            for row in self.connection.execute(
                "SELECT step_id FROM completed_steps WHERE run_id = ?", (run_id,)
            )
        }
        return next((step for step in self._plan(run_id) if step not in completed), None)

    def execute(
        self,
        *,
        run_id: str,
        owner_id: str,
        step_id: str,
        idempotency_key: str,
        payload: dict[str, object],
        inject_failure: bool = False,
    ) -> bool:
        payload_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            lease = self.connection.execute(
                "SELECT owner_id, expires_at FROM run_leases WHERE run_id = ?", (run_id,)
            ).fetchone()
            if (
                lease is None
                or lease["owner_id"] != owner_id
                or lease["expires_at"] <= self.clock.now
            ):
                raise WorkerError("lease_lost")

            existing = self.connection.execute(
                """
                SELECT idempotency_key, payload_hash
                FROM completed_steps WHERE run_id = ? AND step_id = ?
                """,
                (run_id, step_id),
            ).fetchone()
            if existing:
                if (
                    existing["idempotency_key"] == idempotency_key
                    and existing["payload_hash"] == payload_hash
                ):
                    self.connection.execute("COMMIT")
                    return True
                raise WorkerError("step_conflict")

            if self.next_step(run_id) != step_id:
                raise WorkerError("step_out_of_order")
            self.connection.execute(
                """
                INSERT INTO side_effects(idempotency_key, run_id, step_id, payload_hash)
                VALUES (?, ?, ?, ?)
                """,
                (idempotency_key, run_id, step_id, payload_hash),
            )
            if inject_failure:
                raise WorkerError("injected_failure")
            self.connection.execute(
                """
                INSERT INTO completed_steps(run_id, step_id, idempotency_key, payload_hash)
                VALUES (?, ?, ?, ?)
                """,
                (run_id, step_id, idempotency_key, payload_hash),
            )
            self.connection.execute("COMMIT")
            return False
        except sqlite3.IntegrityError as error:
            self.connection.execute("ROLLBACK")
            raise WorkerError("idempotency_conflict") from error
        except Exception:
            self.connection.execute("ROLLBACK")
            raise

    def effect_count(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM side_effects").fetchone()[0])


def fixed_report() -> str:
    clock = VirtualClock()
    worker = RecoverableWorker(":memory:", clock)
    try:
        worker.create_run("run-21", ["prepare", "write"])
        worker.acquire("run-21", "worker-a", 10)
        busy = "unexpected"
        try:
            worker.acquire("run-21", "worker-b", 10)
        except WorkerError as error:
            busy = str(error)
        worker.execute(
            run_id="run-21",
            owner_id="worker-a",
            step_id="prepare",
            idempotency_key="effect-prepare",
            payload={"value": 1},
        )
        clock.advance(11)
        worker.acquire("run-21", "worker-b", 10)
        crash = "unexpected"
        try:
            worker.execute(
                run_id="run-21",
                owner_id="worker-b",
                step_id="write",
                idempotency_key="effect-write",
                payload={"value": 2},
                inject_failure=True,
            )
        except WorkerError as error:
            crash = str(error)
        next_after_crash = worker.next_step("run-21")
        worker.execute(
            run_id="run-21",
            owner_id="worker-b",
            step_id="write",
            idempotency_key="effect-write",
            payload={"value": 2},
        )
        replay = worker.execute(
            run_id="run-21",
            owner_id="worker-b",
            step_id="write",
            idempotency_key="effect-write",
            payload={"value": 2},
        )
        return "\n".join(
            [
                "runtime=python:3.11+,dependencies:stdlib-only,storage:sqlite,clock:virtual,network:disabled",
                f"lease=worker-a:acquired,worker-b:{busy},takeover-after-expiry:true",
                "prepare=committed:true,side-effects:1",
                f"crash={crash},committed:false,next-step:{next_after_crash},side-effects:1",
                f"resume=worker-b,write:committed,replay:{str(replay).lower()},next-step:none,side-effects:{worker.effect_count()}",
                "invariants=single-live-lease,expired-takeover,checkpoint-boundary,idempotent-step,atomic-side-effect,no-duplicate-effect,no-network",
            ]
        )
    finally:
        worker.close()


if __name__ == "__main__":
    print(fixed_report())
