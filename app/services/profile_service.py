from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.education import Education
from app.models.project import Project
from app.models.skill import Skill
from app.models.user import User
from app.models.work_experience import WorkExperience
from app.schemas.profile import ProfileCreate, ProfileUpdate


async def _load_user(session: AsyncSession, user_id: uuid.UUID) -> User:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.educations),
            selectinload(User.work_experiences),
            selectinload(User.projects),
            selectinload(User.skills),
        )
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile {user_id} not found",
        )
    return user


async def list_profiles(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_profile(session: AsyncSession, data: ProfileCreate) -> User:
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        linkedin_url=data.linkedin_url,
        github_url=data.github_url,
        personal_website=data.personal_website,
        location_country=data.location_country,
        location_province_state=data.location_province_state,
        location_city=data.location_city,
    )

    for edu in data.educations:
        user.educations.append(Education(**edu.model_dump()))

    for we in data.work_experiences:
        user.work_experiences.append(WorkExperience(**we.model_dump()))

    for proj in data.projects:
        user.projects.append(Project(**proj.model_dump()))

    for sk in data.skills:
        user.skills.append(Skill(**sk.model_dump()))

    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A profile with email '{data.email}' already exists",
        )

    return await _load_user(session, user.id)


async def get_profile(session: AsyncSession, user_id: uuid.UUID) -> User:
    return await _load_user(session, user_id)


async def update_profile(
    session: AsyncSession,
    user_id: uuid.UUID,
    data: ProfileUpdate,
) -> User:
    user = await _load_user(session, user_id)

    scalar_fields = [
        "name", "email", "phone",
        "linkedin_url", "github_url", "personal_website",
        "location_country", "location_province_state", "location_city",
    ]
    for field in scalar_fields:
        value = getattr(data, field)
        if value is not None:
            setattr(user, field, value)

    if data.educations is not None:
        user.educations.clear()
        for edu in data.educations:
            user.educations.append(Education(**edu.model_dump()))

    if data.work_experiences is not None:
        user.work_experiences.clear()
        for we in data.work_experiences:
            user.work_experiences.append(WorkExperience(**we.model_dump()))

    if data.projects is not None:
        user.projects.clear()
        for proj in data.projects:
            user.projects.append(Project(**proj.model_dump()))

    if data.skills is not None:
        user.skills.clear()
        for sk in data.skills:
            user.skills.append(Skill(**sk.model_dump()))

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A profile with email '{data.email}' already exists",
        )

    return await _load_user(session, user.id)


async def delete_profile(session: AsyncSession, user_id: uuid.UUID) -> None:
    user = await _load_user(session, user_id)
    await session.delete(user)
    await session.commit()


async def get_resume_text(
    session: AsyncSession, profile_id: uuid.UUID
) -> dict[str, str | int]:
    from datetime import date

    user = await _load_user(session, profile_id)
    parts: list[str] = []

    loc_parts = [
        user.location_city,
        user.location_province_state,
        user.location_country,
    ]
    location = ", ".join(p for p in loc_parts if p)

    parts.append(f"Name: {user.name}")
    parts.append(f"Email: {user.email}")
    parts.append(f"Location: {location}")
    parts.append("")

    if user.skills:
        skill_names = ", ".join(s.skill_name for s in user.skills)
        parts.append(f"Skills: {skill_names}")
        parts.append("")

    if user.work_experiences:
        parts.append("Experience:")
        sorted_we = sorted(
            user.work_experiences,
            key=lambda w: w.start_date,
            reverse=True,
        )
        for w in sorted_we:
            start_str = w.start_date.strftime("%Y-%m") if w.start_date else ""
            end_str = (
                w.end_date.strftime("%Y-%m") if w.end_date else "present"
            )
            desc = (w.description or "")[:100]
            parts.append(
                f"  - {w.job_title} @ {w.company_name} ({start_str} – {end_str})"
            )
            parts.append(f"    {desc}")
        parts.append("")

    if user.educations:
        parts.append("Education:")
        for e in user.educations:
            grad_str = (
                e.graduate_date.strftime("%Y-%m")
                if e.graduate_date
                else ""
            )
            parts.append(
                f"  - {e.degree}, {e.field_of_study} — {e.institution_name} ({grad_str})"
            )
        parts.append("")

    if user.projects:
        parts.append("Projects:")
        for p in user.projects:
            start_str = p.start_date.strftime("%Y-%m") if p.start_date else ""
            end_str = (
                p.end_date.strftime("%Y-%m") if p.end_date else "present"
            )
            desc = (p.description or "")[:80]
            parts.append(
                f"  - {p.project_title} ({start_str} – {end_str}): {desc}"
            )
        parts.append("")

    today = date.today()
    total_months = 0
    for w in user.work_experiences:
        if w.start_date:
            end = w.end_date or today
            total_months += (end.year - w.start_date.year) * 12 + (
                end.month - w.start_date.month
            )
    yoe = round(total_months / 12, 1) if total_months else 0
    parts.append(f"YOE: {yoe} years professional")

    resume_text = "\n".join(parts)
    token_estimate = len(resume_text) // 4
    return {"resume_text": resume_text, "token_estimate": token_estimate}
