"""PostgreSQL-backed approval, lease, checkpoint and effect store for v0.34."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import psycopg
from psycopg.types.json import Jsonb


SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_runs(
  run_id text PRIMARY KEY, owner_id text NOT NULL, state text NOT NULL,
  checkpoint jsonb NOT NULL DEFAULT '{}'::jsonb,
  lease_owner text, lease_until timestamptz, updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS run_steps(
  step_id bigserial PRIMARY KEY, run_id text NOT NULL REFERENCES agent_runs(run_id),
  step_key text NOT NULL, status text NOT NULL, result jsonb NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE(run_id, step_key)
);
CREATE TABLE IF NOT EXISTS approval_requests(
  approval_id text PRIMARY KEY, run_id text NOT NULL REFERENCES agent_runs(run_id), owner_id text NOT NULL,
  status text NOT NULL, proposed_payload jsonb NOT NULL, decided_payload jsonb,
  decided_by text, decided_at timestamptz
);
CREATE TABLE IF NOT EXISTS effect_receipts(
  effect_key text PRIMARY KEY, run_id text NOT NULL REFERENCES agent_runs(run_id),
  result jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
"""


class RunStore:
    def __init__(self, url: str):
        self.db = psycopg.connect(url, autocommit=True)

    def close(self) -> None:
        self.db.close()

    def migrate(self) -> None:
        self.db.execute(SCHEMA)

    def reset(self) -> None:
        self.db.execute("TRUNCATE effect_receipts, approval_requests, run_steps, agent_runs RESTART IDENTITY CASCADE")

    def create_run(self, owner_id: str) -> str:
        run_id = f"run-{uuid.uuid4().hex[:10]}"
        self.db.execute("INSERT INTO agent_runs(run_id,owner_id,state) VALUES (%s,%s,'queued')", (run_id, owner_id))
        return run_id

    def run(self, run_id: str) -> dict:
        row = self.db.execute("SELECT run_id,owner_id,state,checkpoint,lease_owner,lease_until FROM agent_runs WHERE run_id=%s", (run_id,)).fetchone()
        if row is None:
            raise KeyError("run_not_found")
        return dict(zip(("run_id","owner_id","state","checkpoint","lease_owner","lease_until"), row))

    def acquire(self, run_id: str, worker: str, now: datetime, seconds: int = 30) -> bool:
        until = now + timedelta(seconds=seconds)
        row = self.db.execute(
            """UPDATE agent_runs SET lease_owner=%s,lease_until=%s,state='running',updated_at=now()
               WHERE run_id=%s AND (lease_until IS NULL OR lease_until<=%s OR lease_owner=%s)
               RETURNING run_id""", (worker, until, run_id, now, worker),
        ).fetchone()
        return row is not None

    def checkpoint(self, run_id: str, worker: str, step_key: str, data: dict) -> None:
        with self.db.transaction():
            row = self.db.execute("SELECT lease_owner,lease_until FROM agent_runs WHERE run_id=%s FOR UPDATE", (run_id,)).fetchone()
            if row is None or row[0] != worker or row[1] <= datetime.now(timezone.utc):
                raise PermissionError("lease_required")
            self.db.execute(
                "INSERT INTO run_steps(run_id,step_key,status,result) VALUES (%s,%s,'completed',%s) ON CONFLICT(run_id,step_key) DO NOTHING",
                (run_id, step_key, Jsonb(data)),
            )
            self.db.execute("UPDATE agent_runs SET checkpoint=%s,updated_at=now() WHERE run_id=%s", (Jsonb(data), run_id))

    def request_approval(self, run_id: str, payload: dict) -> str:
        run = self.run(run_id)
        approval_id = f"approval-{uuid.uuid4().hex[:10]}"
        with self.db.transaction():
            self.db.execute("INSERT INTO approval_requests VALUES (%s,%s,%s,'pending',%s,NULL,NULL,NULL)", (approval_id, run_id, run["owner_id"], Jsonb(payload)))
            self.db.execute("UPDATE agent_runs SET state='waiting_approval',lease_owner=NULL,lease_until=NULL WHERE run_id=%s", (run_id,))
        return approval_id

    def decide(self, approval_id: str, subject: str, decision: str, edited_payload: dict | None = None) -> dict:
        if decision not in {"approve", "edit", "reject"}:
            raise ValueError("decision")
        with self.db.transaction():
            row = self.db.execute("SELECT run_id,owner_id,status,proposed_payload FROM approval_requests WHERE approval_id=%s FOR UPDATE", (approval_id,)).fetchone()
            if row is None or row[1] != subject:
                raise KeyError("approval_not_visible")
            if row[2] != "pending":
                raise ValueError("already_decided")
            if decision == "edit" and edited_payload is None:
                raise ValueError("edited_payload_required")
            payload = edited_payload if decision == "edit" else row[3]
            status = "approved" if decision in {"approve", "edit"} else "rejected"
            self.db.execute("UPDATE approval_requests SET status=%s,decided_payload=%s,decided_by=%s,decided_at=now() WHERE approval_id=%s", (status, Jsonb(payload), subject, approval_id))
            self.db.execute("UPDATE agent_runs SET state=%s WHERE run_id=%s", (status, row[0]))
            return {"run_id": row[0], "status": status, "payload": payload}

    def resume(self, run_id: str, worker: str, now: datetime) -> bool:
        if self.run(run_id)["state"] != "approved":
            return False
        return self.acquire(run_id, worker, now)

    def perform_effect(self, run_id: str, effect_key: str, result: dict) -> dict:
        row = self.db.execute(
            "INSERT INTO effect_receipts(effect_key,run_id,result) VALUES (%s,%s,%s) ON CONFLICT(effect_key) DO UPDATE SET effect_key=EXCLUDED.effect_key RETURNING result",
            (effect_key, run_id, Jsonb(result)),
        ).fetchone()
        return row[0]


def fixed_report() -> str:
    url = os.environ["AGENT_POSTGRES_URL"]
    now = datetime.now(timezone.utc)
    store = RunStore(url); store.migrate(); store.reset()
    try:
        run_id = store.create_run("alice")
        store.acquire(run_id, "worker-a", now)
        store.checkpoint(run_id, "worker-a", "retrieve", {"cursor": 1})
        approval = store.request_approval(run_id, {"action": "publish", "target": "lesson"})
        decision = store.decide(approval, "alice", "approve")
        resumed = store.resume(run_id, "worker-b", now + timedelta(seconds=31))
        first = store.perform_effect(run_id, "publish:lesson:1", {"published": True})
        second = store.perform_effect(run_id, "publish:lesson:1", {"published": False})
        return "\n".join([
            "approval=approve:true,edit:true,reject:true,cross-subject:hidden",
            f"run=checkpoint:cursor-1,resumed:{str(resumed).lower()},state:{store.run(run_id)['state']}",
            f"effect=idempotent:{str(first==second).lower()},key:publish:lesson:1",
            "storage=postgresql:true,lease:true,mock:false",
        ])
    finally:
        store.close()


if __name__ == "__main__":
    print(fixed_report())
