from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication
from app.schemas.application_schema import (
    JobApplicationBatchItem,
    JobApplicationCreate,
    JobApplicationUpdate,
)


async def create_application(
    session: AsyncSession,
    data: JobApplicationCreate,
) -> JobApplication:
    """Insert a new job application. Raises ValueError on duplicate apply_url."""
    apply_url_str = str(data.apply_url).rstrip("/")

    existing = await session.execute(
        select(JobApplication).where(JobApplication.apply_url == apply_url_str)
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError("apply_url already exists")

    app = JobApplication(
        job_title=data.job_title,
        company_name=data.company_name,
        apply_url=apply_url_str,
        date_year=data.date_year,
        date_month=data.date_month,
        date_day=data.date_day,
        job_description=data.job_description,
        yoe=data.yoe,
        skill_set=data.skill_set,
    )
    session.add(app)
    await session.commit()
    await session.refresh(app)
    return app


async def create_applications_batch(
    session: AsyncSession,
    items: list[JobApplicationBatchItem],
) -> tuple[int, list[str]]:
    """
    Insert multiple applications in a single transaction.
    On conflict (apply_url exists): update job_description, yoe, skill_set.
    Returns (logged_count, failed_urls).
    """
    logged = 0
    failed: list[str] = []

    for item in items:
        apply_url_str = str(item.apply_url).strip().rstrip("/")
        if not apply_url_str:
            failed.append(item.apply_url)
            continue

        existing = await session.execute(
            select(JobApplication).where(JobApplication.apply_url == apply_url_str)
        )
        app = existing.scalar_one_or_none()

        if app is not None:
            app.job_title = item.job_title
            app.company_name = item.company_name
            app.date_year = item.date_year
            app.date_month = item.date_month
            app.date_day = item.date_day
            app.job_description = item.job_description or ""
            app.yoe = int(item.yoe)
            app.skill_set = item.skill_set
            app.updated_at = datetime.now(timezone.utc)
            logged += 1
        else:
            try:
                new_app = JobApplication(
                    job_title=item.job_title,
                    company_name=item.company_name,
                    apply_url=apply_url_str,
                    date_year=item.date_year,
                    date_month=item.date_month,
                    date_day=item.date_day,
                    job_description=item.job_description or "",
                    yoe=int(item.yoe),
                    skill_set=item.skill_set,
                )
                session.add(new_app)
                logged += 1
            except Exception:
                failed.append(apply_url_str)

    await session.commit()
    return logged, failed


async def get_application(
    session: AsyncSession,
    application_id: UUID,
) -> JobApplication:
    """Return a single application by id. Raises ValueError if not found."""
    result = await session.execute(
        select(JobApplication).where(JobApplication.id == application_id)
    )
    app = result.scalar_one_or_none()
    if app is None:
        raise ValueError("not found")
    return app


async def list_application_urls(session: AsyncSession) -> list[str]:
    """Return all apply_url values only. Used for URL dedup."""
    stmt = select(JobApplication.apply_url).order_by(
        JobApplication.date_year.desc(),
        JobApplication.date_month.desc(),
        JobApplication.date_day.desc(),
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def dedup_urls(
    session: AsyncSession,
    urls: list[str],
) -> tuple[list[str], list[str]]:
    """
    Given a list of URLs from a search run, return two lists:
      - new_urls: not yet in job_applications
      - applied_urls: already in job_applications
    Uses a single indexed query — never loads full records.
    """
    if not urls:
        return [], []
    stmt = select(JobApplication.apply_url).where(
        JobApplication.apply_url.in_(urls)
    )
    result = await session.execute(stmt)
    applied_set = set(result.scalars().all())
    new_urls = [u for u in urls if u not in applied_set]
    applied_urls = [u for u in urls if u in applied_set]
    return new_urls, applied_urls


async def list_applications(
    session: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> list[JobApplication]:
    """Return all applications ordered by (date_year, date_month, date_day) desc."""
    stmt = (
        select(JobApplication)
        .order_by(
            JobApplication.date_year.desc(),
            JobApplication.date_month.desc(),
            JobApplication.date_day.desc(),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def count_applications(session: AsyncSession) -> int:
    stmt = select(func.count()).select_from(JobApplication)
    result = await session.execute(stmt)
    return result.scalar_one()


async def update_application(
    session: AsyncSession,
    application_id: UUID,
    data: JobApplicationUpdate,
) -> JobApplication:
    """Update only the fields present in data (interview, offer, rejected).
    Raises ValueError if not found."""
    app = await get_application(session, application_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)

    app.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(app)
    return app


async def delete_application(
    session: AsyncSession,
    application_id: UUID,
) -> JobApplication:
    """Delete and return the application. Raises ValueError if not found."""
    app = await get_application(session, application_id)
    await session.delete(app)
    await session.commit()
    return app
