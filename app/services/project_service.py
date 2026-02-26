from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.schemas.profile import ProjectCreate, ProjectUpdate


async def _get_user_or_404(session: AsyncSession, profile_id: uuid.UUID) -> User:
    result = await session.execute(select(User).where(User.id == profile_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile {profile_id} not found",
        )
    return user


async def _get_project_or_404(
    session: AsyncSession, profile_id: uuid.UUID, project_id: uuid.UUID
) -> Project:
    result = await session.execute(
        select(Project).where(
            Project.id == project_id, Project.user_id == profile_id
        )
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found for profile {profile_id}",
        )
    return project


async def list_projects(
    session: AsyncSession, profile_id: uuid.UUID
) -> list[Project]:
    await _get_user_or_404(session, profile_id)
    result = await session.execute(
        select(Project)
        .where(Project.user_id == profile_id)
        .order_by(Project.start_date.desc())
    )
    return list(result.scalars().all())


async def get_project(
    session: AsyncSession, profile_id: uuid.UUID, project_id: uuid.UUID
) -> Project:
    return await _get_project_or_404(session, profile_id, project_id)


async def create_project(
    session: AsyncSession, profile_id: uuid.UUID, data: ProjectCreate
) -> Project:
    await _get_user_or_404(session, profile_id)
    project = Project(user_id=profile_id, **data.model_dump())
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def update_project(
    session: AsyncSession,
    profile_id: uuid.UUID,
    project_id: uuid.UUID,
    data: ProjectUpdate,
) -> Project:
    project = await _get_project_or_404(session, profile_id, project_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    if project.end_date is not None and project.end_date < project.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be >= start_date",
        )

    await session.commit()
    await session.refresh(project)
    return project


async def delete_project(
    session: AsyncSession, profile_id: uuid.UUID, project_id: uuid.UUID
) -> None:
    project = await _get_project_or_404(session, profile_id, project_id)
    await session.delete(project)
    await session.commit()
