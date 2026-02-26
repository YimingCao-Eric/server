from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.profile import (
    WorkExperienceCreate,
    WorkExperienceResponse,
    WorkExperienceUpdate,
)
from app.services import work_experience_service

router = APIRouter(
    prefix="/profiles/{profile_id}/work-experiences",
    tags=["Work Experiences"],
)


@router.get(
    "",
    response_model=list[WorkExperienceResponse],
    summary="List all work experiences for a profile",
)
async def list_work_experiences(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> list[WorkExperienceResponse]:
    items = await work_experience_service.list_work_experiences(session, profile_id)
    return [WorkExperienceResponse.model_validate(i) for i in items]


@router.get(
    "/{work_experience_id}",
    response_model=WorkExperienceResponse,
    summary="Get a single work experience entry",
)
async def get_work_experience(
    profile_id: uuid.UUID,
    work_experience_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> WorkExperienceResponse:
    item = await work_experience_service.get_work_experience(
        session, profile_id, work_experience_id
    )
    return WorkExperienceResponse.model_validate(item)


@router.post(
    "",
    response_model=WorkExperienceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a work experience entry to a profile",
)
async def create_work_experience(
    profile_id: uuid.UUID,
    data: WorkExperienceCreate,
    session: AsyncSession = Depends(get_session),
) -> WorkExperienceResponse:
    item = await work_experience_service.create_work_experience(
        session, profile_id, data
    )
    return WorkExperienceResponse.model_validate(item)


@router.put(
    "/{work_experience_id}",
    response_model=WorkExperienceResponse,
    summary="Update a work experience entry",
)
async def update_work_experience(
    profile_id: uuid.UUID,
    work_experience_id: uuid.UUID,
    data: WorkExperienceUpdate,
    session: AsyncSession = Depends(get_session),
) -> WorkExperienceResponse:
    item = await work_experience_service.update_work_experience(
        session, profile_id, work_experience_id, data
    )
    return WorkExperienceResponse.model_validate(item)


@router.delete(
    "/{work_experience_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a work experience entry",
)
async def delete_work_experience(
    profile_id: uuid.UUID,
    work_experience_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await work_experience_service.delete_work_experience(
        session, profile_id, work_experience_id
    )
    return {"detail": f"Work experience {work_experience_id} deleted successfully"}
