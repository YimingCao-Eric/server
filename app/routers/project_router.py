from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.profile import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project_service

router = APIRouter(
    prefix="/profiles/{profile_id}/projects",
    tags=["Projects"],
)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List all projects for a profile",
)
async def list_projects(
    profile_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> list[ProjectResponse]:
    items = await project_service.list_projects(session, profile_id)
    return [ProjectResponse.model_validate(i) for i in items]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a single project entry",
)
async def get_project(
    profile_id: uuid.UUID,
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    item = await project_service.get_project(session, profile_id, project_id)
    return ProjectResponse.model_validate(item)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a project entry to a profile",
)
async def create_project(
    profile_id: uuid.UUID,
    data: ProjectCreate,
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    item = await project_service.create_project(session, profile_id, data)
    return ProjectResponse.model_validate(item)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project entry",
)
async def update_project(
    profile_id: uuid.UUID,
    project_id: uuid.UUID,
    data: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    item = await project_service.update_project(
        session, profile_id, project_id, data
    )
    return ProjectResponse.model_validate(item)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a project entry",
)
async def delete_project(
    profile_id: uuid.UUID,
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    await project_service.delete_project(session, profile_id, project_id)
    return {"detail": f"Project {project_id} deleted successfully"}
