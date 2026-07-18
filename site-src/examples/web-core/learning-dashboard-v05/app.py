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
        completed_lessons=8,
        completed_hours=7.5,
        status="按计划推进",
        next_milestone="让前后端契约保持一致",
    ),
    "afei": LearningSummary(
        learner_id="afei",
        learner_name="阿飞",
        description="已经完成 Web 起步，正在用 TypeScript 收紧页面的数据边界。",
        completed_lessons=13,
        completed_hours=10.0,
        status="本周已完成",
        next_milestone="把记录保存到数据库",
    ),
}

app = FastAPI(
    title="学习进度报告器 API",
    version="0.5.0",
    description="Web Core v0.5：用 OpenAPI 与 TypeScript 维护前后端契约。",
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.5.0"}


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


@app.get("/api/demo-contract-drift", include_in_schema=False)
def demo_contract_drift() -> JSONResponse:
    """Return an intentionally invalid payload for the local lesson demo only."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "learner_id": "contract-drift",
            "learner_name": "契约漂移示例",
            "description": "这个端点故意绕过 response_model，只用于观察前端拒绝错误数据。",
            "completed_lessons": 8,
            "completed_hours": "七个半小时",
            "status": "按计划推进",
            "next_milestone": "恢复正确类型",
        },
    )


WEB_ROOT = Path(__file__).resolve().parent
app.mount("/", StaticFiles(directory=WEB_ROOT, html=True), name="dashboard")
