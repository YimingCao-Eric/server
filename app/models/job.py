from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    website: Mapped[str] = mapped_column(String(50), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    post_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    job_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    apply_url: Mapped[str | None] = mapped_column(String(), nullable=True)
    easy_apply: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    external_id: Mapped[str | None] = mapped_column(String(), nullable=True)
    search_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    search_location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Matching pipeline fields
    match_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    match_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    matched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), nullable=False
    )

    # JD extraction fields
    extracted_yoe: Mapped[float | None] = mapped_column(Float, nullable=True)
    extracted_skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True
    )
    extracted_education: Mapped[str | None] = mapped_column(String(20), nullable=True)
    education_field: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(10), nullable=True)
    fit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    req_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    required_skills: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    nice_to_have_skills: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    critical_skills: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Content dedup hash
    raw_description_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Gate/skip reason (salary_gate, critical_skills_gate, education_gate, etc.)
    skipped_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Additional job metadata
    dismissed: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    job_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    remote_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(50), nullable=True)
    visa_sponsorship_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    jd_incomplete: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    recurring_unapplied: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )

    __table_args__ = (
        Index("ix_jobs_website", "website"),
        Index("ix_jobs_job_title", "job_title"),
        Index("ix_jobs_company", "company"),
        Index("ix_jobs_job_url", "job_url", unique=True, postgresql_where=job_url.isnot(None)),
        Index("ix_jobs_dedup", "website", "job_title", "company"),
        Index("ix_jobs_dismissed", "dismissed"),
        Index("ix_jobs_external_id", "external_id"),
        Index("ix_jobs_raw_description_hash", "raw_description_hash"),
        Index("ix_jobs_skipped_reason", "skipped_reason"),
    )
