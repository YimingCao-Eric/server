from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.education import Education
from app.models.user import User
from app.schemas.profile import EducationCreate, EducationUpdate


async def _get_user_or_404(session: AsyncSession, profile_id: uuid.UUID) -> User:
    result = await session.execute(select(User).where(User.id == profile_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile {profile_id} not found",
        )
    return user


async def _get_education_or_404(
    session: AsyncSession, profile_id: uuid.UUID, education_id: uuid.UUID
) -> Education:
    result = await session.execute(
        select(Education).where(
            Education.id == education_id, Education.user_id == profile_id
        )
    )
    education = result.scalar_one_or_none()
    if education is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education {education_id} not found for profile {profile_id}",
        )
    return education


async def list_educations(
    session: AsyncSession, profile_id: uuid.UUID
) -> list[Education]:
    await _get_user_or_404(session, profile_id)
    result = await session.execute(
        select(Education)
        .where(Education.user_id == profile_id)
        .order_by(Education.start_date.desc())
    )
    return list(result.scalars().all())


async def get_education(
    session: AsyncSession, profile_id: uuid.UUID, education_id: uuid.UUID
) -> Education:
    return await _get_education_or_404(session, profile_id, education_id)


async def create_education(
    session: AsyncSession, profile_id: uuid.UUID, data: EducationCreate
) -> Education:
    await _get_user_or_404(session, profile_id)
    education = Education(user_id=profile_id, **data.model_dump())
    session.add(education)
    await session.commit()
    await session.refresh(education)
    return education


async def update_education(
    session: AsyncSession,
    profile_id: uuid.UUID,
    education_id: uuid.UUID,
    data: EducationUpdate,
) -> Education:
    education = await _get_education_or_404(session, profile_id, education_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(education, field, value)

    if education.graduate_date < education.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="graduate_date must be >= start_date",
        )

    await session.commit()
    await session.refresh(education)
    return education


async def delete_education(
    session: AsyncSession, profile_id: uuid.UUID, education_id: uuid.UUID
) -> None:
    education = await _get_education_or_404(session, profile_id, education_id)
    await session.delete(education)
    await session.commit()
