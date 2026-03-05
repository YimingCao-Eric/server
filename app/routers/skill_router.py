from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.profile import SkillCreate, SkillResponse, SkillUpdate
from app.services import skill_service

router = APIRouter(
    prefix="/profiles/{profile_id}/skills",
    tags=["Skills"],
)


@router.get(
    "",
    response_model=list[SkillResponse],
    summary="List all skills for a profile",
)
async def list_skills(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> list[SkillResponse]:
    items = await skill_service.list_skills(session, profile_id)
    return [SkillResponse.model_validate(i) for i in items]


@router.get(
    "/{skill_id}",
    response_model=SkillResponse,
    summary="Get a single skill entry",
)
async def get_skill(
    profile_id: uuid.UUID,
    skill_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> SkillResponse:
    item = await skill_service.get_skill(session, profile_id, skill_id)
    return SkillResponse.model_validate(item)


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill entry to a profile",
)
async def create_skill(
    profile_id: uuid.UUID,
    data: SkillCreate,
    session: AsyncSession = Depends(get_session),
) -> SkillResponse:
    item = await skill_service.create_skill(session, profile_id, data)
    return SkillResponse.model_validate(item)


@router.put(
    "/{skill_id}",
    response_model=SkillResponse,
    summary="Update a skill entry",
)
async def update_skill(
    profile_id: uuid.UUID,
    skill_id: uuid.UUID,
    data: SkillUpdate,
    session: AsyncSession = Depends(get_session),
) -> SkillResponse:
    item = await skill_service.update_skill(
        session, profile_id, skill_id, data
    )
    return SkillResponse.model_validate(item)


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a skill entry",
)
async def delete_skill(
    profile_id: uuid.UUID,
    skill_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await skill_service.delete_skill(session, profile_id, skill_id)
    return {"detail": f"Skill {skill_id} deleted successfully"}
