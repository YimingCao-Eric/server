from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.schemas.job_schema import JobIngestRequest


async def _check_duplicate(session: AsyncSession, data: JobIngestRequest) -> None:
    if data.source_url:
        stmt = select(Job.id).where(Job.source_url == data.source_url)
    else:
        stmt = select(Job.id).where(
            Job.website == data.website,
            Job.job_title == data.job_title,
            Job.company == data.company,
        )

    result = await session.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate job posting already exists",
        )


async def ingest_job(session: AsyncSession, data: JobIngestRequest) -> Job:
    await _check_duplicate(session, data)

    job = Job(**data.model_dump())
    session.add(job)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(job)
    return job
