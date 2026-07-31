from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

from knowledge_service import KnowledgeService

ROOT = Path(__file__).resolve().parent


def create_app(service: KnowledgeService | None = None) -> FastAPI:
    store = service or KnowledgeService()
    app = FastAPI(title="Intelligent learning assistant", version="0.30.0")
    app.state.service = store

    def subject(value: str | None) -> str:
        if not value:
            raise HTTPException(401, "需要主体", headers={"WWW-Authenticate": "Subject"})
        return value

    def translate(error: Exception) -> None:
        if isinstance(error, KeyError):
            raise HTTPException(404, "资源不可见") from error
        raise HTTPException(409, str(error)) from error

    @app.middleware("http")
    async def count_requests(request, call_next):
        store.counters["requests"] += 1
        return await call_next(request)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return (ROOT / "index.html").read_text()

    @app.get("/assets/app.js")
    def frontend() -> FileResponse:
        return FileResponse(ROOT / "dist" / "app.js", media_type="text/javascript")

    @app.get("/health/live")
    def live() -> dict:
        return {"status": "live"}

    @app.get("/health/ready")
    def ready() -> dict:
        return {"status": "ready", "prompt_version": "grounded-answer-v1"}

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics() -> str:
        return store.metrics()

    @app.post("/api/knowledge-sources", status_code=201)
    def create_source(payload: dict, x_subject_id: str | None = Header(default=None)) -> dict:
        return store.create_source(subject(x_subject_id), str(payload.get("name", "")).strip())

    @app.post("/api/knowledge-sources/{source_id}/versions", status_code=202)
    def upload(source_id: str, payload: dict, x_subject_id: str | None = Header(default=None)) -> dict:
        try:
            return store.upload(subject(x_subject_id), source_id, payload.get("kind", ""), payload.get("content", ""))
        except (KeyError, ValueError) as error:
            translate(error)

    @app.get("/api/knowledge-sources/{source_id}/versions")
    def versions(source_id: str, x_subject_id: str | None = Header(default=None)) -> list[dict]:
        try:
            return store.list_versions(subject(x_subject_id), source_id)
        except KeyError as error:
            translate(error)

    @app.get("/api/ingestion-jobs/{job_id}")
    def job(job_id: str, x_subject_id: str | None = Header(default=None)) -> dict:
        owner = subject(x_subject_id)
        result = store.jobs.get(job_id)
        if result is None:
            raise HTTPException(404, "作业不可见")
        try:
            store._source(owner, result["source_id"])
        except KeyError as error:
            translate(error)
        return result

    @app.post("/api/knowledge-sources/{source_id}/deactivate")
    def deactivate(source_id: str, x_subject_id: str | None = Header(default=None)) -> dict:
        try:
            return store.deactivate(subject(x_subject_id), source_id)
        except KeyError as error:
            translate(error)

    @app.post("/api/knowledge-sources/{source_id}/rollback")
    def rollback(source_id: str, payload: dict, x_subject_id: str | None = Header(default=None)) -> dict:
        try:
            return store.rollback(subject(x_subject_id), source_id, int(payload["version"]))
        except (KeyError, ValueError) as error:
            translate(error)

    @app.post("/api/retrieval/debug")
    def retrieval(payload: dict, x_subject_id: str | None = Header(default=None)) -> dict:
        return store.debug_retrieval(subject(x_subject_id), payload.get("query", ""), min(int(payload.get("limit", 5)), 20))

    @app.post("/api/chat/sessions", status_code=201)
    def create_session(x_subject_id: str | None = Header(default=None)) -> dict:
        return store.create_session(subject(x_subject_id))

    @app.post("/api/chat/sessions/{session_id}/messages", status_code=201)
    def chat(session_id: str, payload: dict, x_subject_id: str | None = Header(default=None)) -> dict:
        try:
            return store.chat(subject(x_subject_id), session_id, payload.get("question", ""))
        except KeyError as error:
            translate(error)

    return app


app = create_app()
