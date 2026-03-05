from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=text("gen_random_uuid()"),
        primary_key=True,
    )
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    apply_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    date_year: Mapped[int] = mapped_column(Integer, nullable=False)
    date_month: Mapped[int] = mapped_column(Integer, nullable=False)
    date_day: Mapped[int] = mapped_column(Integer, nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    yoe: Mapped[int] = mapped_column(
        Integer, server_default=text("0"), nullable=False
    )
    skill_set: Mapped[list[str]] = mapped_column(
        ARRAY(Text), server_default=text("'{}'::text[]"), nullable=False
    )
    interview: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    offer: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    rejected: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
