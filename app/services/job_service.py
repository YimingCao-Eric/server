from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.schemas.job_schema import JobIngestRequest, JobMatchResultWrite


async def _find_duplicate(session: AsyncSession, data: JobIngestRequest) -> Job | None:
    if data.job_url:
        stmt = select(Job).where(Job.job_url == data.job_url)
    else:
        stmt = select(Job).where(
            Job.website == data.website,
            Job.job_title == data.job_title,
            Job.company == data.company,
        )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def ingest_job(
    session: AsyncSession, data: JobIngestRequest
) -> tuple[Job, bool]:
    existing = await _find_duplicate(session, data)
    if existing is not None:
        return existing, True

    job = Job(**data.model_dump())
    session.add(job)

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    await session.refresh(job)
    return job, False


async def store_match_result(
    session: AsyncSession,
    data: JobMatchResultWrite,
) -> Job:
    """
    Store pre-computed match result from OpenClaw onto an existing jobs row.
    Sets matched_at = now(). Raises ValueError if job_id not found.
    Does not call any LLM.
    """
    stmt = select(Job).where(Job.id == data.job_id)
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    if job is None:
        raise ValueError(f"Job {data.job_id} not found")

    job.match_level = data.match_level
    job.match_reason = data.match_reason
    job.extracted_skills = data.extracted_skills
    job.extracted_education = data.extracted_education
    job.extracted_yoe = data.extracted_yoe
    job.matched_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(job)
    return job
