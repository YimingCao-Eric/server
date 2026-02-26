from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.work_experience import WorkExperience
from app.schemas.profile import WorkExperienceCreate, WorkExperienceUpdate


async def _get_user_or_404(session: AsyncSession, profile_id: uuid.UUID) -> User:
    result = await session.execute(select(User).where(User.id == profile_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile {profile_id} not found",
        )
    return user


async def _get_work_experience_or_404(
    session: AsyncSession, profile_id: uuid.UUID, work_experience_id: uuid.UUID
) -> WorkExperience:
    result = await session.execute(
        select(WorkExperience).where(
            WorkExperience.id == work_experience_id,
            WorkExperience.user_id == profile_id,
        )
    )
    we = result.scalar_one_or_none()
    if we is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work experience {work_experience_id} not found for profile {profile_id}",
        )
    return we


async def list_work_experiences(
    session: AsyncSession, profile_id: uuid.UUID
) -> list[WorkExperience]:
    await _get_user_or_404(session, profile_id)
    result = await session.execute(
        select(WorkExperience)
        .where(WorkExperience.user_id == profile_id)
        .order_by(WorkExperience.start_date.desc())
    )
    return list(result.scalars().all())


async def get_work_experience(
    session: AsyncSession, profile_id: uuid.UUID, work_experience_id: uuid.UUID
) -> WorkExperience:
    return await _get_work_experience_or_404(session, profile_id, work_experience_id)


async def create_work_experience(
    session: AsyncSession, profile_id: uuid.UUID, data: WorkExperienceCreate
) -> WorkExperience:
    await _get_user_or_404(session, profile_id)
    we = WorkExperience(user_id=profile_id, **data.model_dump())
    session.add(we)
    await session.commit()
    await session.refresh(we)
    return we


async def update_work_experience(
    session: AsyncSession,
    profile_id: uuid.UUID,
    work_experience_id: uuid.UUID,
    data: WorkExperienceUpdate,
) -> WorkExperience:
    we = await _get_work_experience_or_404(session, profile_id, work_experience_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(we, field, value)

    if we.end_date is not None and we.end_date < we.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be >= start_date",
        )

    await session.commit()
    await session.refresh(we)
    return we


async def delete_work_experience(
    session: AsyncSession, profile_id: uuid.UUID, work_experience_id: uuid.UUID
) -> None:
    we = await _get_work_experience_or_404(session, profile_id, work_experience_id)
    await session.delete(we)
    await session.commit()
