from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import pipeline

router = APIRouter(tags=["分层任务"])


class JobBody(BaseModel):
    domain_id: int = Field(..., description="主题域编号")


class BypassJobBody(BaseModel):
    domain_id: int = Field(..., description="主题域编号")
    simulate_failure: bool = Field(False, description="模拟旁路失败，用于验证主旁路失败域隔离")


@router.get("/jobs")
def list_jobs(domain_id: int | None = None, lane: str | None = None):
    return pipeline.list_jobs(domain_id, lane)


@router.post("/jobs/paste-to-detail")
def paste_to_detail(body: JobBody):
    try:
        job = pipeline.run_paste_to_detail(body.domain_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return job


@router.post("/jobs/detail-to-summary")
def detail_to_summary(body: JobBody):
    try:
        job = pipeline.run_detail_to_summary(body.domain_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return job


@router.post("/jobs/detail-to-category-summary")
def detail_to_category_summary(body: BypassJobBody):
    """品类旁路任务：独立任务写独立旁路表，失败不影响主汇总与主对账。"""
    try:
        return pipeline.run_detail_to_category_summary(
            body.domain_id, simulate_failure=body.simulate_failure
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
