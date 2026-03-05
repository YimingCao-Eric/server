from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
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
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    extracted_yoe: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracted_skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True
    )
    extracted_education: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Content dedup hash
    raw_description_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_jobs_website", "website"),
        Index("ix_jobs_job_title", "job_title"),
        Index("ix_jobs_company", "company"),
        Index("ix_jobs_source_url", "source_url", unique=True, postgresql_where=source_url.isnot(None)),
        Index("ix_jobs_dedup", "website", "job_title", "company"),
    )
