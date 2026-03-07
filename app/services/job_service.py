from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import and_

from app.models.job import Job
from app.schemas.job_schema import (
    JobIngestRequest,
    JobMatchResultBatchItem,
    JobMatchResultWrite,
    JobPartialUpdate,
    JobReviewResponse,
)


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
    job.skipped_reason = data.skipped_reason
    job.matched_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(job)
    return job


async def store_match_results_batch(
    session: AsyncSession,
    items: list[JobMatchResultBatchItem],
) -> tuple[int, list[str]]:
    """
    Store match results for multiple jobs in a single transaction.
    Skips job_ids not found; returns (updated_count, failed_job_ids).
    """
    updated = 0
    failed: list[str] = []
    now = datetime.now(timezone.utc)

    for item in items:
        stmt = select(Job).where(Job.id == item.job_id)
        result = await session.execute(stmt)
        job = result.scalar_one_or_none()
        if job is None:
            failed.append(str(item.job_id))
            continue

        job.match_level = item.match_level
        job.match_reason = item.match_reason
        job.matched_at = now
        if item.confidence is not None:
            job.confidence = item.confidence
        if item.fit_score is not None:
            job.fit_score = item.fit_score
        if item.req_coverage is not None:
            job.req_coverage = item.req_coverage
        if item.extracted_skills is not None:
            job.extracted_skills = item.extracted_skills
        if item.required_skills is not None:
            job.required_skills = item.required_skills
        if item.nice_to_have_skills is not None:
            job.nice_to_have_skills = item.nice_to_have_skills
        if item.critical_skills is not None:
            job.critical_skills = item.critical_skills
        if item.extracted_yoe is not None:
            job.extracted_yoe = item.extracted_yoe
        if item.extracted_education is not None:
            job.extracted_education = item.extracted_education
        if item.education_field is not None:
            job.education_field = item.education_field
        if item.seniority_level is not None:
            job.seniority_level = item.seniority_level
        if item.remote_type is not None:
            job.remote_type = item.remote_type
        if item.visa_required is not None:
            job.visa_sponsorship_required = item.visa_required
        if item.salary_min is not None:
            job.salary_min = item.salary_min
        if item.salary_max is not None:
            job.salary_max = item.salary_max
        if item.job_type is not None:
            job.job_type = item.job_type
        if item.industry is not None:
            job.industry = item.industry
        job.jd_incomplete = item.jd_incomplete
        if item.skipped_reason is not None:
            job.skipped_reason = item.skipped_reason

        updated += 1

    await session.commit()
    return updated, failed


async def update_job_partial(
    session: AsyncSession,
    job_id: UUID,
    data: JobPartialUpdate,
) -> Job | None:
    """
    Partial update of a job (dismissed, recurring_unapplied, is_active).
    Returns the job if found, None otherwise.
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await session.execute(stmt)
    job = result.scalar_one_or_none()
    if job is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await session.commit()
    await session.refresh(job)
    return job


async def batch_dismiss(
    session: AsyncSession,
    job_ids: list[UUID],
) -> int:
    """
    Set dismissed=true for all jobs with id in job_ids.
    Returns count of rows updated.
    """
    if not job_ids:
        return 0
    stmt = update(Job).where(Job.id.in_(job_ids)).values(dismissed=True)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount or 0


def _date_range_clause(
    date_range: str | None,
    date_from: date | None,
    date_to: date | None,
):
    """Build SQLAlchemy clause for created_at filtering. Uses jobs.created_at (UTC)."""
    clauses = []
    if date_range == "today":
        start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        clauses.append(Job.created_at >= start)
    elif date_range == "last_7_days":
        start = datetime.now(timezone.utc) - timedelta(days=7)
        clauses.append(Job.created_at >= start)
    elif date_range == "last_30_days":
        start = datetime.now(timezone.utc) - timedelta(days=30)
        clauses.append(Job.created_at >= start)
    if date_from is not None:
        start_dt = datetime.combine(date_from, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        clauses.append(Job.created_at >= start_dt)
    if date_to is not None:
        end_dt = datetime.combine(date_to, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )
        clauses.append(Job.created_at <= end_dt)
    return and_(*clauses) if clauses else None


async def get_jobs_filtered(
    session: AsyncSession,
    *,
    dismissed: bool | None = False,
    skipped_reason: str | None = None,
    match_level: str | None = None,
    date_range: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    company: str | None = None,
) -> list[JobReviewResponse]:
    """
    Query jobs with filters for Step 3 review handler.
    Default: excluded dismissed (dismissed=False).
    """
    stmt = select(Job)
    conditions = []

    # Default: exclude dismissed. dismissed=true -> only dismissed; dismissed=false/None -> exclude
    if dismissed is True:
        conditions.append(Job.dismissed == True)
    else:
        conditions.append(Job.dismissed == False)
    if skipped_reason is not None:
        conditions.append(Job.skipped_reason == skipped_reason)
    if match_level is not None:
        conditions.append(Job.match_level == match_level)
    if company is not None and company.strip():
        conditions.append(Job.company.ilike(f"%{company.strip()}%"))

    date_clause = _date_range_clause(date_range, date_from, date_to)
    if date_clause is not None:
        conditions.append(date_clause)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.order_by(Job.created_at.desc())
    result = await session.execute(stmt)
    jobs = result.scalars().all()

    return [
        JobReviewResponse(
            id=j.id,
            job_title=j.job_title,
            company=j.company,
            location=j.location,
            match_level=j.match_level,
            fit_score=j.fit_score,
            req_coverage=j.req_coverage,
            skipped_reason=j.skipped_reason,
            extracted_yoe=j.extracted_yoe,
            seniority_level=j.seniority_level,
            required_skills=j.required_skills,
            critical_skills=j.critical_skills,
            salary_min=j.salary_min,
            salary_max=j.salary_max,
            dismissed=j.dismissed,
            created_at=j.created_at,
            job_url=j.job_url,
            easy_apply=j.easy_apply,
        )
        for j in jobs
    ]


async def get_match_results_summary(
    session: AsyncSession,
    *,
    date_range: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict:
    """
    Return match-results summary with gate breakdown (including salary_gate,
    critical_skills_gate) and match_level counts.
    """
    date_clause = _date_range_clause(date_range, date_from, date_to)

    # Total scraped
    count_stmt = select(func.count(Job.id)).select_from(Job)
    if date_clause is not None:
        count_stmt = count_stmt.where(date_clause)
    total_scraped = (await session.execute(count_stmt)).scalar() or 0

    # Gate breakdown: count by skipped_reason (includes salary_gate, critical_skills_gate)
    gate_names = [
        "internship_gate",
        "visa_gate",
        "education_gate",
        "yoe_gate",
        "salary_gate",
        "critical_skills_gate",
        "keyword_filter",
    ]
    gate_breakdown: dict[str, int] = {g: 0 for g in gate_names}

    gate_stmt = (
        select(Job.skipped_reason, func.count(Job.id))
        .where(Job.skipped_reason.is_not(None))
        .group_by(Job.skipped_reason)
    )
    if date_clause is not None:
        gate_stmt = gate_stmt.where(date_clause)
    gate_result = await session.execute(gate_stmt)
    for row in gate_result:
        gate_breakdown[row[0]] = gate_breakdown.get(row[0], 0) + row[1]

    # Match level counts
    match_levels = [
        "strong_match",
        "possible_match",
        "stretch_match",
        "weak_match",
    ]
    match_level_counts: dict[str, int] = {m: 0 for m in match_levels}
    match_level_counts["skipped"] = 0

    level_stmt = select(Job.match_level, func.count(Job.id)).group_by(Job.match_level)
    if date_clause is not None:
        level_stmt = level_stmt.where(date_clause)
    level_result = await session.execute(level_stmt)
    for row in level_result:
        ml = row[0]
        if ml in match_level_counts:
            match_level_counts[ml] = row[1]
        elif ml is None or ml in (
            "irrelevant",
            "fully_matched",
            "half_matched",
            "little_matched",
        ):
            match_level_counts["skipped"] += row[1]
        else:
            match_level_counts["skipped"] += row[1]

    return {
        "total_scraped": total_scraped,
        "total_deduped": total_scraped,
        "gate_breakdown": gate_breakdown,
        "match_level_counts": match_level_counts,
    }
