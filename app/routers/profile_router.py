from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a full user profile",
)
async def create_profile(
    data: ProfileCreate,
    session: AsyncSession = Depends(get_session),
) -> ProfileResponse:
    user = await profile_service.create_profile(session, data)
    return ProfileResponse.model_validate(user)


@router.get(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Get a user profile by ID",
)
async def get_profile(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ProfileResponse:
    user = await profile_service.get_profile(session, profile_id)
    return ProfileResponse.model_validate(user)


@router.put(
    "/{profile_id}",
    response_model=ProfileResponse,
    summary="Update a user profile",
)
async def update_profile(
    profile_id: uuid.UUID,
    data: ProfileUpdate,
    session: AsyncSession = Depends(get_session),
) -> ProfileResponse:
    user = await profile_service.update_profile(session, profile_id, data)
    return ProfileResponse.model_validate(user)


@router.delete(
    "/{profile_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user profile",
)
async def delete_profile(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await profile_service.delete_profile(session, profile_id)
    return {"detail": f"Profile {profile_id} deleted successfully"}
