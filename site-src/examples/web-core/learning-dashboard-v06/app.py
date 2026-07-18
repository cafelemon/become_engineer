from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path as ApiPath, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from database import LearnerNotFoundError, LearningDatabase, LearningSummaryRow


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

    learner_id: Annotated[str, Field(pattern=r"^[a-z0-9-]{3,32}$")]
    hours: Annotated[float, Field(gt=0, le=24)]
    note: Annotated[str, Field(min_length=1, max_length=200)]


class StudySessionCreated(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: int
    learner_id: str
    hours: float
    note: str


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


WEB_ROOT = Path(__file__).resolve().parent


def create_app(database_path: Path | None = None) -> FastAPI:
    path = database_path or Path(
        os.environ.get("LEARNING_DB_PATH", WEB_ROOT / "data" / "learning.sqlite3")
    )
    database = LearningDatabase(path)

    api = FastAPI(
        title="学习进度报告器 API",
        version="0.6.0",
        description="Web Core v0.6：用 SQLite 保存学习者与学习时段。",
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
            "version": "0.6.0",
            "storage": "sqlite",
            "schema_version": schema_version,
        }

    @api.get("/api/learning-summary/{learner_id}", response_model=LearningSummary)
    def learning_summary(
        learner_id: Annotated[
            str,
            ApiPath(pattern=r"^[a-z0-9-]{3,32}$"),
        ],
    ) -> LearningSummary:
        try:
            return summary_model(database.get_summary(learner_id))
        except LearnerNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这位学习者") from error
        except sqlite3.Error as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="数据库暂时不可用",
            ) from error

    @api.post(
        "/api/study-sessions",
        response_model=StudySessionCreated,
        status_code=status.HTTP_201_CREATED,
    )
    def create_study_session(payload: StudySessionInput) -> StudySessionCreated:
        try:
            row = database.add_session(payload.learner_id, payload.hours, payload.note)
        except LearnerNotFoundError as error:
            raise HTTPException(status_code=404, detail="没有找到这位学习者") from error
        except sqlite3.Error as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="学习时段没有保存，数据库已回滚",
            ) from error

        return StudySessionCreated(
            session_id=row.session_id,
            learner_id=row.learner_id,
            hours=row.hours,
            note=row.note,
        )

    @api.get("/api/demo-unavailable", include_in_schema=False)
    def demo_unavailable() -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "数据库暂时不可用，请稍后重试"},
        )

    api.mount("/", StaticFiles(directory=WEB_ROOT, html=True), name="dashboard")
    return api


app = create_app()
