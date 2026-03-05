from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.report_schema import ReportResponse, ReportStoreRequest
from app.services import report_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])

_latest_report: ReportResponse | None = None


@router.post("/store", response_model=ReportResponse, status_code=200)
async def store_report(data: ReportStoreRequest) -> ReportResponse:
    """
    Receive pre-written report from OpenClaw and store in memory.
    Does not run any LLM. Returns the stored report with generated_at timestamp.
    """
    global _latest_report
    _latest_report = ReportResponse(
        report_text=data.report_text,
        applications_analysed=data.applications_analysed,
        generated_at=datetime.now(timezone.utc),
    )
    return _latest_report


@router.post("/generate", response_model=ReportResponse, status_code=200)
async def generate_report(
    session: AsyncSession = Depends(get_session),
) -> ReportResponse:
    global _latest_report
    try:
        report = await report_service.generate_report(session)
        _latest_report = report
        return report
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/latest", response_model=ReportResponse)
async def get_latest_report() -> ReportResponse:
    if _latest_report is None:
        raise HTTPException(
            status_code=404,
            detail="No report stored yet. Use POST /reports/store (Phase 1 / OpenClaw) or POST /reports/generate (Phase 2/3 / backend LLM).",
        )
    return _latest_report
