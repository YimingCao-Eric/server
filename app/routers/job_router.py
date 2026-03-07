from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.job_schema import (
    BatchDismissRequest,
    BatchDismissResponse,
    JobIngestRequest,
    JobIngestResponse,
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResultBatchItem,
    JobMatchResultBatchResponse,
    JobMatchResultResponse,
    JobMatchResultWrite,
    JobPartialUpdate,
    JobRecommendation,
    JobReviewResponse,
    JobUpdateResponse,
    MatchResultsSummary,
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
    "/match-results/batch",
    response_model=JobMatchResultBatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Store match results for multiple jobs (batch)",
)
async def store_match_results_batch(
    data: list[JobMatchResultBatchItem],
    session: AsyncSession = Depends(get_session),
) -> JobMatchResultBatchResponse:
    """
    Batch store pre-computed match results. Skips job_ids not found.
    Returns updated count and list of failed job_ids.
    """
    updated, failed = await job_service.store_match_results_batch(session, data)
    return JobMatchResultBatchResponse(updated=updated, failed=failed)


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


@router.get(
    "/",
    response_model=list[JobReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Query jobs with filters (Step 3 review handler)",
)
async def get_jobs(
    session: AsyncSession = Depends(get_session),
    dismissed: bool | None = Query(
        None,
        description="dismissed=true: only dismissed; default: exclude dismissed",
    ),
    skipped_reason: str | None = Query(
        None,
        description="Filter by gate: salary_gate, critical_skills_gate, etc.",
    ),
    match_level: str | None = Query(
        None,
        description="Filter by match_level: stretch_match, weak_match",
    ),
    date_range: str | None = Query(
        None,
        description="today | last_7_days | last_30_days",
    ),
    date_from: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    company: str | None = Query(None, description="Company name (ILIKE match)"),
) -> list[JobReviewResponse]:
    dismissed_filter = dismissed if dismissed is not None else False
    return await job_service.get_jobs_filtered(
        session,
        dismissed=dismissed_filter,
        skipped_reason=skipped_reason,
        match_level=match_level,
        date_range=date_range,
        date_from=date_from,
        date_to=date_to,
        company=company,
    )


@router.get(
    "/match-results/summary",
    response_model=MatchResultsSummary,
    status_code=status.HTTP_200_OK,
    summary="Get match-results summary with gate breakdown",
)
async def get_match_results_summary(
    session: AsyncSession = Depends(get_session),
    date_range: str | None = Query(
        None,
        description="today | last_7_days | last_30_days",
    ),
    date_from: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="End date (YYYY-MM-DD)"),
) -> MatchResultsSummary:
    result = await job_service.get_match_results_summary(
        session,
        date_range=date_range,
        date_from=date_from,
        date_to=date_to,
    )
    return MatchResultsSummary(**result)


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger an external scraping workflow",
)
async def trigger_scrape(data: ScrapeRequest) -> ScrapeResponse:
    result = await scrape_service.trigger_scrape(data)
    return ScrapeResponse(**result)


@router.put(
    "/batch/dismiss",
    response_model=BatchDismissResponse,
    status_code=status.HTTP_200_OK,
    summary="Dismiss multiple jobs by id",
)
async def batch_dismiss_jobs(
    data: BatchDismissRequest,
    session: AsyncSession = Depends(get_session),
) -> BatchDismissResponse:
    """Set dismissed=true for all jobs with id in job_ids."""
    count = await job_service.batch_dismiss(session, data.job_ids)
    return BatchDismissResponse(dismissed=count)


@router.put(
    "/{job_id}",
    response_model=JobUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Partial update of a job (dismiss, restore, etc.)",
)
async def update_job(
    job_id: uuid.UUID,
    data: JobPartialUpdate,
    session: AsyncSession = Depends(get_session),
) -> JobUpdateResponse:
    """Update only the fields present in the request body."""
    job = await job_service.update_job_partial(session, job_id, data)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobUpdateResponse(id=job.id, updated=True)

