from __future__ import annotations

import logging
from datetime import datetime, timezone

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.job_application import JobApplication
from app.schemas.report_schema import ReportResponse

logger = logging.getLogger(__name__)


async def generate_report(session: AsyncSession) -> ReportResponse:
    """Generate a weekly job search report from application data using Claude."""
    stmt = (
        select(JobApplication)
        .order_by(
            JobApplication.date_year.desc(),
            JobApplication.date_month.desc(),
            JobApplication.date_day.desc(),
        )
    )
    result = await session.execute(stmt)
    applications = list(result.scalars().all())

    applications = applications[:100]

    lines: list[str] = []
    for app in applications:
        skills_preview = (app.skill_set or [])[:5]
        line = (
            f"{app.date_year}-{app.date_month:02d}-{app.date_day:02d} | "
            f"{app.company_name} | {app.job_title} | "
            f"yoe={app.yoe} | skills={skills_preview} | "
            f"interview={app.interview} | offer={app.offer} | rejected={app.rejected}"
        )
        lines.append(line)

    data_summary = "\n".join(lines) if lines else "(no applications)"

    system_prompt = (
        "You are a career coach generating a weekly job search performance report. "
        "Be specific, data-driven, and concise. Do not invent data not present in the input. "
        "Structure your response with clear sections."
    )
    user_prompt = f"""Generate a weekly job search report based on this application data.
Each line is: date | company | role | yoe_required | skills | interview | offer | rejected

{data_summary}

Write the report with these sections:
1. SUMMARY — total applications, interviews, offers, rejections this week
2. INTERVIEW PERFORMANCE — which companies responded, conversion rate
3. REJECTION PATTERNS — common traits in rejected applications
   (seniority, skills mentioned, YOE gaps)
4. OFFERS — any offers received and next steps
5. SKILL GAPS — skills that appear frequently in rejected/non-matching jobs
   that the candidate lacks
6. RECOMMENDATIONS — 3 specific actions for next week"""

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        response_text = response.content[0].text
    except Exception as e:
        logger.error("Report generation failed: %s", e)
        raise RuntimeError(f"Report generation failed: {e}") from e

    return ReportResponse(
        report_text=response_text,
        generated_at=datetime.now(timezone.utc),
        applications_analysed=len(applications),
    )
