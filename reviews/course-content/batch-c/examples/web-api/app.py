from __future__ import annotations

from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class LearningSummary(BaseModel):
    learner_id: str
    learner_name: str
    completed_lessons: int
    planned_lessons: int
    completed_hours: float
    status: Literal["起步中", "按计划推进", "本周已完成"]


SUMMARIES = {
    "xiaoma": LearningSummary(
        learner_id="xiaoma",
        learner_name="小码",
        completed_lessons=4,
        planned_lessons=7,
        completed_hours=6.5,
        status="按计划推进",
    ),
    "afei": LearningSummary(
        learner_id="afei",
        learner_name="阿飞",
        completed_lessons=7,
        planned_lessons=7,
        completed_hours=9.0,
        status="本周已完成",
    ),
}

app = FastAPI(title="学习进度报告器 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8768", "http://localhost:8768"],
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/learning-summary/{learner_id}", response_model=LearningSummary)
def learning_summary(
    learner_id: Annotated[str, Path(pattern=r"^[a-z0-9-]{3,32}$")],
) -> LearningSummary:
    summary = SUMMARIES.get(learner_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="没有找到这位学习者")
    return summary
