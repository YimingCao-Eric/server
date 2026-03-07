from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date, datetime, timezone
from uuid import UUID

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.job import Job
from app.models.skill import Skill
from app.models.work_experience import WorkExperience
from app.schemas.job_schema import (
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResult,
    JobRecommendation,
    SkillHistogramItem,
)

logger = logging.getLogger(__name__)

# User context (loaded from profile in pipeline)
USER_HIGHEST_DEGREE = "master"


def _normalise_description(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _hash_description(text: str) -> str:
    return hashlib.sha256(_normalise_description(text).encode()).hexdigest()


async def _extract_jd_fields(
    job_description: str, client: anthropic.AsyncAnthropic
) -> dict:
    user_msg = f"""Extract the following fields from this job description.
Respond ONLY with a JSON object, no other text:

{{
  "skill_set": ["list of required technical skills and tools"],
  "education_requirement": "bachelor" or "master" or "phd" or "none",
  "yoe_required": <integer years required, or null if not stated>
}}

Rules:
- skill_set: only concrete technologies, languages, frameworks, tools.
  Do NOT include soft skills or vague terms like "communication".
- education_requirement: use the MINIMUM required degree.
  If no degree is mentioned, use "none".
- yoe_required: extract the minimum years of experience required.
  If a range is given (e.g. "3-5 years"), use the lower bound.
  If not mentioned, use null.

Job description:
{job_description}"""

    try:
        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=300,
            system="You are a precise job description parser. Extract structured data from job descriptions. Always respond with valid JSON only — no markdown, no explanation, no preamble.",
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text
        data = json.loads(text)
        return {
            "skill_set": data.get("skill_set", []),
            "education_requirement": data.get("education_requirement", "none"),
            "yoe_required": data.get("yoe_required"),
        }
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        logger.warning("JD extraction parse failure: %s", e)
        return {"skill_set": [], "education_requirement": "none", "yoe_required": None}


def _education_gate(extracted_education: str) -> bool:
    if extracted_education in ("bachelor", "master", "none"):
        return True
    if extracted_education == "phd":
        return False
    return True


async def _get_profile_yoe(
    session: AsyncSession,
    profile_id: UUID,
) -> int:
    """
    Compute total professional YOE from work_experiences for a given profile.
    Sums months across all non-null date ranges, converts to whole years.
    Returns 0 if no work experiences found.
    """
    stmt = select(WorkExperience).where(WorkExperience.user_id == profile_id)
    result = await session.execute(stmt)
    experiences = result.scalars().all()

    if not experiences:
        return 0

    total_months = 0
    today = date.today()
    for exp in experiences:
        if exp.start_date is None:
            continue
        end = exp.end_date if exp.end_date else today
        months = (end.year - exp.start_date.year) * 12 + (
            end.month - exp.start_date.month
        )
        total_months += max(0, months)

    return total_months // 12


def _yoe_gate(extracted_yoe: int | None, profile_yoe: int) -> bool:
    """
    Returns True (pass) if the job's YOE requirement is within range.
    Gate fails if (yoe_required - profile_yoe) > 1.
    """
    if extracted_yoe is None:
        return True
    return (extracted_yoe - profile_yoe) <= 1


def _keyword_prefilter(job_skills: list[str], profile_skills: list[str]) -> bool:
    job_set = {s.strip().lower() for s in job_skills if s.strip()}
    profile_set = {s.strip().lower() for s in profile_skills if s.strip()}
    if len(job_set & profile_set) == 0:
        return False
    return True


async def _llm_skill_match(
    job_skills: list[str],
    profile_skills: list[str],
    job_title: str,
    client: anthropic.AsyncAnthropic,
) -> dict:
    user_msg = f"""Match the candidate's skills against the job's required skills.

Job title: {job_title}
Required skills: {job_skills}
Candidate skills: {profile_skills}

Respond ONLY with a JSON object:
{{
  "match_level": "fully_matched" or "half_matched" or "little_matched" or "irrelevant",
  "match_reason": "one sentence explaining the match level"
}}

Scoring rules:
- fully_matched:  80-100% of required skills covered by candidate
- half_matched:   50-79%  of required skills covered
- little_matched: 25-49%  covered
- irrelevant:     0-24%   covered or completely wrong domain"""

    try:
        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=150,
            system="You are a precise job-candidate skill matcher. Always respond with valid JSON only — no markdown, no explanation, no preamble.",
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text
        data = json.loads(text)
        return {
            "match_level": data.get("match_level", "irrelevant"),
            "match_reason": data.get("match_reason", "parse error"),
        }
    except (json.JSONDecodeError, IndexError, KeyError):
        return {"match_level": "irrelevant", "match_reason": "parse error"}


async def run_match_pipeline(
    session: AsyncSession,
    job_ids: list[UUID],
    profile_id: UUID,
    force_rematch: bool = False,
) -> JobMatchResponse:
    # Derive YOE from profile — replaces hardcoded USER_YOE_YEARS
    profile_yoe = await _get_profile_yoe(session, profile_id)

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    result_stmt = select(Skill).where(Skill.user_id == profile_id)
    skills_result = await session.execute(result_stmt)
    skills = list(skills_result.scalars().all())
    profile_skill_names = [s.skill_name for s in skills]

    results: list[JobMatchResult] = []
    fully_matched = 0
    half_matched = 0
    little_matched = 0
    irrelevant = 0
    skipped = 0

    for job_id in job_ids:
        job_result = await session.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if job is None:
            continue

        if job.matched_at is not None and not force_rematch:
            results.append(
                JobMatchResult(
                    job_id=job.id,
                    match_level=job.match_level or "irrelevant",
                    match_reason=job.match_reason or "",
                    already_matched=True,
                    skipped_reason=None,
                )
            )
            if job.match_level == "fully_matched":
                fully_matched += 1
            elif job.match_level == "half_matched":
                half_matched += 1
            elif job.match_level == "little_matched":
                little_matched += 1
            else:
                irrelevant += 1
            continue

        # Compute hash for this job's description
        new_hash = _hash_description(job.job_description)

        # Skip LLM extraction only if:
        #   - hash matches what's stored on THIS row (same description as before)
        #   - AND extracted fields are already populated on this row
        #   - AND force_rematch is False
        # In this case, reuse the stored extracted fields.
        # Still run gates and skill match below — this row is not yet matched.
        skip_extraction = (
            job.raw_description_hash == new_hash
            and job.extracted_skills is not None
            and job.extracted_education is not None
            and not force_rematch
        )

        if not skip_extraction:
            extracted = await _extract_jd_fields(job.job_description, client)
            job.extracted_skills = extracted.get("skill_set") or []
            job.extracted_education = (
                extracted.get("education_requirement") or "none"
            ).lower()
            job.extracted_yoe = extracted.get("yoe_required")
            job.raw_description_hash = new_hash

        if not _education_gate(job.extracted_education):
            job.match_level = "irrelevant"
            job.match_reason = "education_gate"
            job.skipped_reason = "education_gate"
            job.matched_at = datetime.now(timezone.utc)
            results.append(
                JobMatchResult(
                    job_id=job.id,
                    match_level="irrelevant",
                    match_reason="education_gate",
                    already_matched=False,
                    skipped_reason="education_gate",
                )
            )
            irrelevant += 1
            skipped += 1
            continue

        if not _yoe_gate(job.extracted_yoe, profile_yoe):
            job.match_level = "irrelevant"
            job.match_reason = "yoe_gate"
            job.skipped_reason = "yoe_gate"
            job.matched_at = datetime.now(timezone.utc)
            results.append(
                JobMatchResult(
                    job_id=job.id,
                    match_level="irrelevant",
                    match_reason="yoe_gate",
                    already_matched=False,
                    skipped_reason="yoe_gate",
                )
            )
            irrelevant += 1
            skipped += 1
            continue

        if not _keyword_prefilter(job.extracted_skills or [], profile_skill_names):
            job.match_level = "irrelevant"
            job.match_reason = "keyword_filter"
            job.skipped_reason = "keyword_filter"
            job.matched_at = datetime.now(timezone.utc)
            results.append(
                JobMatchResult(
                    job_id=job.id,
                    match_level="irrelevant",
                    match_reason="keyword_filter",
                    already_matched=False,
                    skipped_reason="keyword_filter",
                )
            )
            irrelevant += 1
            skipped += 1
            continue

        llm_result = await _llm_skill_match(
            job.extracted_skills or [],
            profile_skill_names,
            job.job_title,
            client,
        )
        job.match_level = llm_result["match_level"]
        job.match_reason = llm_result["match_reason"]
        job.matched_at = datetime.now(timezone.utc)

        results.append(
            JobMatchResult(
                job_id=job.id,
                match_level=job.match_level,
                match_reason=job.match_reason,
                already_matched=False,
                skipped_reason=None,
            )
        )
        if job.match_level == "fully_matched":
            fully_matched += 1
        elif job.match_level == "half_matched":
            half_matched += 1
        elif job.match_level == "little_matched":
            little_matched += 1
        else:
            irrelevant += 1

    await session.commit()

    return JobMatchResponse(
        results=results,
        total=len(results),
        fully_matched=fully_matched,
        half_matched=half_matched,
        little_matched=little_matched,
        irrelevant=irrelevant,
        skipped=skipped,
    )


async def get_recommendations(
    session: AsyncSession, profile_id: UUID
) -> list[JobRecommendation]:
    from sqlalchemy import case

    stmt = (
        select(Job)
        .where(
            Job.match_level.in_(["fully_matched", "half_matched"]),
            Job.is_active == True,
        )
        .order_by(
            case((Job.match_level == "fully_matched", 0), else_=1),
            Job.post_datetime.desc().nullslast(),
        )
    )
    result = await session.execute(stmt)
    jobs = list(result.scalars().all())
    return [
        JobRecommendation(
            id=j.id,
            job_title=j.job_title,
            company=j.company,
            location=j.location or "",
            job_url=j.job_url,
            match_level=j.match_level or "irrelevant",
            match_reason=j.match_reason or "",
            post_datetime=j.post_datetime,
        )
        for j in jobs
    ]


async def get_skill_histogram(session: AsyncSession) -> list[SkillHistogramItem]:
    stmt = select(Job).where(Job.extracted_skills.is_not(None))
    result = await session.execute(stmt)
    jobs = list(result.scalars().all())
    counts: dict[str, int] = {}
    for job in jobs:
        for skill in job.extracted_skills or []:
            norm = skill.strip().lower()
            if norm:
                counts[norm] = counts.get(norm, 0) + 1
    sorted_items = sorted(counts.items(), key=lambda x: -x[1])
    return [SkillHistogramItem(skill=k, count=v) for k, v in sorted_items]
