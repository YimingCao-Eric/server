from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.application_schema import (
    ApplicationCountResponse,
    DedupRequest,
    DedupResponse,
    JobApplicationBatchItem,
    JobApplicationBatchResponse,
    JobApplicationCreate,
    JobApplicationRead,
    JobApplicationUpdate,
)
from app.services import application_service

router = APIRouter(prefix="/jobs/applications", tags=["applications"])


@router.post(
    "",
    response_model=JobApplicationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job application",
)
async def create_application(
    data: JobApplicationCreate,
    session: AsyncSession = Depends(get_session),
) -> JobApplicationRead:
    try:
        app = await application_service.create_application(session, data)
        return JobApplicationRead.model_validate(app)
    except ValueError as e:
        if "apply_url" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="apply_url already exists",
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/batch",
    response_model=JobApplicationBatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch create job applications",
)
async def create_applications_batch(
    data: list[JobApplicationBatchItem],
    session: AsyncSession = Depends(get_session),
) -> JobApplicationBatchResponse:
    """
    Insert multiple applications in a single transaction.
    On conflict (apply_url exists): update existing record.
    """
    logged, failed = await application_service.create_applications_batch(
        session, data
    )
    return JobApplicationBatchResponse(logged=logged, failed=failed)


@router.post(
    "/dedup",
    response_model=DedupResponse,
    status_code=status.HTTP_200_OK,
    summary="Server-side URL dedup",
)
async def dedup_urls(
    data: DedupRequest,
    session: AsyncSession = Depends(get_session),
) -> DedupResponse:
    """
    Server-side URL dedup for Step 2.
    Send today's searched job URLs; receive back only the new ones.
    Replaces the pattern of downloading all apply_urls and filtering locally.
    """
    new_urls, applied_urls = await application_service.dedup_urls(
        session, data.urls
    )
    return DedupResponse(
        new_urls=new_urls,
        already_applied=applied_urls,
        total_input=len(data.urls),
        new_count=len(new_urls),
        applied_count=len(applied_urls),
    )


@router.get(
    "/count",
    response_model=ApplicationCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Count job applications",
)
async def count_applications(
    session: AsyncSession = Depends(get_session),
) -> ApplicationCountResponse:
    count = await application_service.count_applications(session)
    return ApplicationCountResponse(count=count)


@router.get(
    "/urls",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="List all applied URLs",
)
async def list_application_urls(
    session: AsyncSession = Depends(get_session),
) -> list[str]:
    """Return all applied URLs for Step 2 URL dedup. No job_description included."""
    return await application_service.list_application_urls(session)


@router.get(
    "",
    response_model=list[JobApplicationRead],
    status_code=status.HTTP_200_OK,
    summary="List all job applications",
)
async def list_applications(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[JobApplicationRead]:
    apps = await application_service.list_applications(session, limit, offset)
    return [JobApplicationRead.model_validate(a) for a in apps]


@router.get(
    "/{application_id}",
    response_model=JobApplicationRead,
    status_code=status.HTTP_200_OK,
    summary="Get a single job application",
)
async def get_application(
    application_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> JobApplicationRead:
    try:
        app = await application_service.get_application(session, application_id)
        return JobApplicationRead.model_validate(app)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{application_id}",
    response_model=JobApplicationRead,
    status_code=status.HTTP_200_OK,
    summary="Update job application flags",
)
async def update_application(
    application_id: uuid.UUID,
    data: JobApplicationUpdate,
    session: AsyncSession = Depends(get_session),
) -> JobApplicationRead:
    try:
        app = await application_service.update_application(
            session, application_id, data
        )
        return JobApplicationRead.model_validate(app)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
