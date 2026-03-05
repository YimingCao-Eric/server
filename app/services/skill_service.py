from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.models.user import User
from app.schemas.profile import SkillCreate, SkillUpdate


async def _get_user_or_404(session: AsyncSession, profile_id: uuid.UUID) -> User:
    result = await session.execute(select(User).where(User.id == profile_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile {profile_id} not found",
        )
    return user


async def _get_skill_or_404(
    session: AsyncSession, profile_id: uuid.UUID, skill_id: uuid.UUID
) -> Skill:
    result = await session.execute(
        select(Skill).where(
            Skill.id == skill_id,
            Skill.user_id == profile_id,
        )
    )
    skill = result.scalar_one_or_none()
    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_id} not found for profile {profile_id}",
        )
    return skill


async def list_skills(
    session: AsyncSession, profile_id: uuid.UUID
) -> list[Skill]:
    await _get_user_or_404(session, profile_id)
    result = await session.execute(
        select(Skill).where(Skill.user_id == profile_id).order_by(Skill.skill_name)
    )
    return list(result.scalars().all())


async def create_skill(
    session: AsyncSession, profile_id: uuid.UUID, data: SkillCreate
) -> Skill:
    await _get_user_or_404(session, profile_id)
    skill = Skill(user_id=profile_id, **data.model_dump())
    session.add(skill)
    await session.commit()
    await session.refresh(skill)
    return skill


async def get_skill(
    session: AsyncSession, profile_id: uuid.UUID, skill_id: uuid.UUID
) -> Skill:
    return await _get_skill_or_404(session, profile_id, skill_id)


async def update_skill(
    session: AsyncSession,
    profile_id: uuid.UUID,
    skill_id: uuid.UUID,
    data: SkillUpdate,
) -> Skill:
    skill = await _get_skill_or_404(session, profile_id, skill_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(skill, field, value)

    await session.commit()
    await session.refresh(skill)
    return skill


async def delete_skill(
    session: AsyncSession, profile_id: uuid.UUID, skill_id: uuid.UUID
) -> None:
    skill = await _get_skill_or_404(session, profile_id, skill_id)
    await session.delete(skill)
    await session.commit()
