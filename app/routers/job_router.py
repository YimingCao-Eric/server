from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.job_schema import (
    JobIngestRequest,
    JobIngestResponse,
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResultResponse,
    JobMatchResultWrite,
    JobRecommendation,
    SkillHistogramItem,
)
from app.schemas.job_scrape_schema import ScrapeRequest, ScrapeResponse
from app.services import job_service, matching_service, scrape_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/ingest",
    response_model=JobIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest a job posting from an external collector",
)
async def ingest_job(
    data: JobIngestRequest,
    session: AsyncSession = Depends(get_session),
) -> JobIngestResponse:
    job, already_exists = await job_service.ingest_job(session, data)
    return JobIngestResponse(id=job.id, already_exists=already_exists)


@router.post(
    "/match-results",
    response_model=JobMatchResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Store pre-computed match result from OpenClaw",
)
async def store_match_result(
    data: JobMatchResultWrite,
    session: AsyncSession = Depends(get_session),
) -> JobMatchResultResponse:
    """
    Receive pre-computed match result from OpenClaw and store on jobs row.
    Does not run any LLM. Returns 404 if job_id not found.
    """
    try:
        job = await job_service.store_match_result(session, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobMatchResultResponse(
        job_id=job.id,
        stored=True,
        matched_at=job.matched_at,
    )


@router.post(
    "/match",
    response_model=JobMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Run matching pipeline for jobs against a profile",
)
async def run_match(
    data: JobMatchRequest,
    session: AsyncSession = Depends(get_session),
) -> JobMatchResponse:
    return await matching_service.run_match_pipeline(
        session,
        data.job_ids,
        data.profile_id,
        data.force_rematch,
    )


@router.get(
    "/recommendations/{profile_id}",
    response_model=list[JobRecommendation],
    status_code=status.HTTP_200_OK,
    summary="Get job recommendations for a profile",
)
async def get_recommendations(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> list[JobRecommendation]:
    return await matching_service.get_recommendations(session, profile_id)


@router.get(
    "/skill-histogram",
    response_model=list[SkillHistogramItem],
    status_code=status.HTTP_200_OK,
    summary="Get skill frequency histogram from extracted jobs",
)
async def get_skill_histogram(
    session: AsyncSession = Depends(get_session),
) -> list[SkillHistogramItem]:
    return await matching_service.get_skill_histogram(session)


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger an external scraping workflow",
)
async def trigger_scrape(data: ScrapeRequest) -> ScrapeResponse:
    result = await scrape_service.trigger_scrape(data)
    return ScrapeResponse(**result)
