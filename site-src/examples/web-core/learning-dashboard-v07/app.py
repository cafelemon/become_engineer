from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Header, HTTPException, Path as ApiPath, Query, Response, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from database import (
    IdempotencyConflictError,
    LearnerNotFoundError,
    LearningDatabase,
    LearningSummaryRow,
    StudySessionNotFoundError,
    StudySessionRow,
)


class LearningSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    learner_id: str
    learner_name: str
    description: str
    completed_lessons: int
    completed_hours: float
    status: Literal["起步中", "按计划推进", "本周已完成"]
    next_milestone: str


class StudySessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hours: Annotated[float, Field(gt=0, le=24)]
    note: Annotated[str, Field(min_length=1, max_length=200)]


class StudySession(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: int
    learner_id: str
    hours: float
    note: str
    created_at: str


class StudySessionWriteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session: StudySession
    replayed: bool


class StudySessionPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[StudySession]
    next_after_id: int | None


def summary_model(row: LearningSummaryRow) -> LearningSummary:
    return LearningSummary(
        learner_id=row.learner_id,
        learner_name=row.learner_name,
        description=row.description,
        completed_lessons=row.completed_lessons,
        completed_hours=row.completed_hours,
        status=row.status,
        next_milestone=row.next_milestone,
    )


def session_model(row: StudySessionRow) -> StudySession:
    return StudySession(
        session_id=row.session_id,
        learner_id=row.learner_id,
        hours=row.hours,
        note=row.note,
        created_at=row.created_at,
    )


WEB_ROOT = Path(__file__).resolve().parent


def create_app(database_path: Path | None = None) -> FastAPI:
    path = database_path or Path(
        os.environ.get("LEARNING_DB_PATH", WEB_ROOT / "data" / "learning.sqlite3")
    )
    database = LearningDatabase(path)

    api = FastAPI(
        title="学习进度报告器 API",
        version="0.7.0",
        description="Web Core v0.7：REST 资源、游标分页和重复写入保护。",
    )
    api.state.database = database

    @api.get("/api/health")
    def health() -> dict[str, str | int]:
        try:
            schema_version = database.schema_version()
        except sqlite3.Error as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="数据库暂时不可用",
            ) from error
        return {
            "status": "ok",
            "version": "0.7.0",
            "storage": "sqlite",
            "schema_version": schema_version,
        }

    @api.get("/api/learning-summary/{learner_id}", response_model=LearningSummary)
    def learning_summary(
        learner_id: Annotated[str, ApiPath(pattern=r"^[a-z0-9-]{3,32}$")],
    ) -> LearningSummary:
        try:
            return summary_model(database.get_summary(learner_id))
        except LearnerNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这位学习者") from error
        except sqlite3.Error as error:
            raise HTTPException(status_code=503, detail="数据库暂时不可用") from error

    @api.get(
        "/api/learners/{learner_id}/study-sessions",
        response_model=StudySessionPage,
    )
    def list_study_sessions(
        learner_id: Annotated[str, ApiPath(pattern=r"^[a-z0-9-]{3,32}$")],
        limit: Annotated[int, Query(ge=1, le=50)] = 2,
        after_id: Annotated[int, Query(ge=0)] = 0,
    ) -> StudySessionPage:
        try:
            page = database.list_sessions(learner_id, limit=limit, after_id=after_id)
        except LearnerNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这位学习者") from error
        except sqlite3.Error as error:
            raise HTTPException(status_code=503, detail="数据库暂时不可用") from error
        return StudySessionPage(
            items=[session_model(item) for item in page.items],
            next_after_id=page.next_after_id,
        )

    @api.get("/api/study-sessions/{session_id}", response_model=StudySession)
    def get_study_session(
        session_id: Annotated[int, ApiPath(ge=1)],
    ) -> StudySession:
        try:
            return session_model(database.get_session(session_id))
        except StudySessionNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这条学习时段") from error
        except sqlite3.Error as error:
            raise HTTPException(status_code=503, detail="数据库暂时不可用") from error

    @api.post(
        "/api/learners/{learner_id}/study-sessions",
        response_model=StudySessionWriteResult,
        status_code=status.HTTP_201_CREATED,
    )
    def create_study_session(
        learner_id: Annotated[str, ApiPath(pattern=r"^[a-z0-9-]{3,32}$")],
        payload: StudySessionInput,
        response: Response,
        idempotency_key: Annotated[
            str,
            Header(alias="Idempotency-Key", pattern=r"^[A-Za-z0-9._:-]{8,80}$"),
        ],
    ) -> StudySessionWriteResult:
        try:
            row, replayed = database.create_session(
                learner_id,
                payload.hours,
                payload.note,
                idempotency_key,
            )
        except LearnerNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这位学习者") from error
        except IdempotencyConflictError as error:
            raise HTTPException(
                status_code=409,
                detail="这个 Idempotency-Key 已用于另一份请求内容",
            ) from error
        except sqlite3.Error as error:
            raise HTTPException(status_code=503, detail="学习时段没有保存") from error

        response.status_code = status.HTTP_200_OK if replayed else status.HTTP_201_CREATED
        response.headers["Location"] = f"/api/study-sessions/{row.session_id}"
        return StudySessionWriteResult(session=session_model(row), replayed=replayed)

    @api.put("/api/study-sessions/{session_id}", response_model=StudySession)
    def replace_study_session(
        session_id: Annotated[int, ApiPath(ge=1)],
        payload: StudySessionInput,
    ) -> StudySession:
        try:
            return session_model(
                database.replace_session(session_id, payload.hours, payload.note)
            )
        except StudySessionNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这条学习时段") from error
        except sqlite3.Error as error:
            raise HTTPException(status_code=503, detail="学习时段没有更新") from error

    @api.delete(
        "/api/study-sessions/{session_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_study_session(
        session_id: Annotated[int, ApiPath(ge=1)],
    ) -> Response:
        try:
            database.delete_session(session_id)
        except StudySessionNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这条学习时段") from error
        except sqlite3.Error as error:
            raise HTTPException(status_code=503, detail="学习时段没有删除") from error
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @api.get("/api/demo-unavailable", include_in_schema=False)
    def demo_unavailable() -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "数据库暂时不可用"})

    api.mount("/", StaticFiles(directory=WEB_ROOT, html=True), name="dashboard")
    return api


app = create_app()
