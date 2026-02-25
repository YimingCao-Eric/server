from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.education import Education
    from app.models.skill import Skill
    from app.models.work_experience import WorkExperience


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    personal_website: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_province_state: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    location_city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    educations: Mapped[list[Education]] = relationship(
        "Education", back_populates="user", cascade="all, delete-orphan"
    )
    work_experiences: Mapped[list[WorkExperience]] = relationship(
        "WorkExperience", back_populates="user", cascade="all, delete-orphan"
    )
    skills: Mapped[list[Skill]] = relationship(
        "Skill", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_email", "email"),
    )
