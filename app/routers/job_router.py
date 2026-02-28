from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.job_schema import JobIngestRequest, JobIngestResponse
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/ingest",
    response_model=JobIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a job posting from an external collector",
)
async def ingest_job(
    data: JobIngestRequest,
    session: AsyncSession = Depends(get_session),
) -> JobIngestResponse:
    job = await job_service.ingest_job(session, data)
    return JobIngestResponse.model_validate(job)
