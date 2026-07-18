from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path as ApiPath, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict


class LearningSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    learner_id: str
    learner_name: str
    description: str
    completed_lessons: int
    completed_hours: float
    status: Literal["起步中", "按计划推进", "本周已完成"]
    next_milestone: str


SUMMARIES: dict[str, LearningSummary] = {
    "xiaoma": LearningSummary(
        learner_id="xiaoma",
        learner_name="小码",
        description="正在学习 Python 与 Web，希望把练习做成可以展示的作品。",
        completed_lessons=7,
        completed_hours=6.5,
        status="按计划推进",
        next_milestone="完成第一个本地 API",
    ),
    "afei": LearningSummary(
        learner_id="afei",
        learner_name="阿飞",
        description="已经完成 Python 起步，正在补齐浏览器与 API 基础。",
        completed_lessons=12,
        completed_hours=9.0,
        status="本周已完成",
        next_milestone="进入 Web 核心",
    ),
}

app = FastAPI(title="学习进度报告器 API", version="0.4.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.4.0"}


@app.get("/api/learning-summary/{learner_id}", response_model=LearningSummary)
def learning_summary(
    learner_id: Annotated[
        str,
        ApiPath(pattern=r"^[a-z0-9-]{3,32}$"),
    ],
) -> LearningSummary:
    summary = SUMMARIES.get(learner_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="没有找到这位学习者")
    return summary


@app.get("/api/demo-unavailable", include_in_schema=False)
def demo_unavailable() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "服务暂时不可用，请稍后重试"},
    )


WEB_ROOT = Path(__file__).resolve().parent
app.mount("/", StaticFiles(directory=WEB_ROOT, html=True), name="dashboard")
