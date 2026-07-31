from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

from delivery_guard import authorize, classify_content, redact

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="Agent delivery console", version="0.36.0")
runs: dict[str, dict] = {}
approvals: dict[str, dict] = {}


def identity(subject: str | None, role: str | None) -> tuple[str, str]:
    if not subject:
        raise HTTPException(401, "需要身份", headers={"WWW-Authenticate": "Subject"})
    return subject, role or "learner"


def owned_run(run_id: str, subject: str) -> dict:
    run = runs.get(run_id)
    if run is None or run["owner_id"] != subject:
        raise HTTPException(404, "资源不可见")
    return run


@app.get("/", response_class=HTMLResponse)
def index() -> str: return (ROOT / "index.html").read_text()


@app.get("/assets/app.js")
def frontend() -> FileResponse: return FileResponse(ROOT / "dist" / "app.js", media_type="text/javascript")


@app.get("/health/live")
def live() -> dict: return {"status": "live"}


@app.get("/health/ready")
def ready() -> dict: return {"status": "ready", "version": "0.36.0"}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str: return f"agent_runs_total {len(runs)}\nagent_approvals_pending {sum(a['status']=='pending' for a in approvals.values())}\n"


@app.post("/api/agent-runs", status_code=201)
def create_run(payload: dict, x_subject_id: str | None = Header(default=None), x_role: str | None = Header(default=None)) -> dict:
    subject, role = identity(x_subject_id, x_role)
    if not authorize(role, "run:create", subject=subject, owner=subject): raise HTTPException(403, "权限不足")
    run_id = f"run-{uuid.uuid4().hex[:10]}"; content = classify_content(str(payload.get("goal", "")))
    run = {"run_id": run_id, "owner_id": subject, "state": "waiting_approval", "goal": payload.get("goal", ""), "content_boundary": content,
           "steps": [{"name": "authorize", "status": "completed"}, {"name": "plan", "status": "completed"}, {"name": "approval", "status": "waiting"}]}
    approval_id = f"approval-{uuid.uuid4().hex[:10]}"; approvals[approval_id] = {"approval_id": approval_id, "run_id": run_id, "owner_id": subject, "status": "pending"}
    run["approval_id"] = approval_id; runs[run_id] = run; return redact(run)


@app.get("/api/agent-runs/{run_id}")
def get_run(run_id: str, x_subject_id: str | None = Header(default=None), x_role: str | None = Header(default=None)) -> dict:
    subject, role = identity(x_subject_id, x_role); run = owned_run(run_id, subject)
    if not authorize(role, "run:read", subject=subject, owner=run["owner_id"]): raise HTTPException(403, "权限不足")
    return redact(run)


@app.post("/api/approval-requests/{approval_id}/decision")
def decide(approval_id: str, payload: dict, x_subject_id: str | None = Header(default=None), x_role: str | None = Header(default=None)) -> dict:
    subject, role = identity(x_subject_id, x_role); approval = approvals.get(approval_id)
    if approval is None or approval["owner_id"] != subject: raise HTTPException(404, "资源不可见")
    if not authorize(role, "approval:decide-own", subject=subject, owner=approval["owner_id"]): raise HTTPException(403, "权限不足")
    decision = payload.get("decision");
    if decision not in {"approve", "edit", "reject"}: raise HTTPException(422, "无效决定")
    approval["status"] = "approved" if decision in {"approve", "edit"} else "rejected"; run = runs[approval["run_id"]]; run["state"] = approval["status"]
    run["steps"][-1]["status"] = approval["status"]; return {"approval_id": approval_id, "status": approval["status"], "run_state": run["state"]}
