from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.profile import EducationCreate, EducationResponse, EducationUpdate
from app.services import education_service

router = APIRouter(
    prefix="/profiles/{profile_id}/educations",
    tags=["Educations"],
)


@router.get(
    "",
    response_model=list[EducationResponse],
    summary="List all educations for a profile",
)
async def list_educations(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> list[EducationResponse]:
    items = await education_service.list_educations(session, profile_id)
    return [EducationResponse.model_validate(i) for i in items]


@router.get(
    "/{education_id}",
    response_model=EducationResponse,
    summary="Get a single education entry",
)
async def get_education(
    profile_id: uuid.UUID,
    education_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> EducationResponse:
    item = await education_service.get_education(session, profile_id, education_id)
    return EducationResponse.model_validate(item)


@router.post(
    "",
    response_model=EducationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an education entry to a profile",
)
async def create_education(
    profile_id: uuid.UUID,
    data: EducationCreate,
    session: AsyncSession = Depends(get_session),
) -> EducationResponse:
    item = await education_service.create_education(session, profile_id, data)
    return EducationResponse.model_validate(item)


@router.put(
    "/{education_id}",
    response_model=EducationResponse,
    summary="Update an education entry",
)
async def update_education(
    profile_id: uuid.UUID,
    education_id: uuid.UUID,
    data: EducationUpdate,
    session: AsyncSession = Depends(get_session),
) -> EducationResponse:
    item = await education_service.update_education(
        session, profile_id, education_id, data
    )
    return EducationResponse.model_validate(item)


@router.delete(
    "/{education_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an education entry",
)
async def delete_education(
    profile_id: uuid.UUID,
    education_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await education_service.delete_education(session, profile_id, education_id)
    return {"detail": f"Education {education_id} deleted successfully"}
