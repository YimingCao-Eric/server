from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SkillCategory(str, enum.Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    TOOLING = "tooling"
    MACHINE_LEARNING = "machine_learning"
    SOFT_SKILL = "soft_skill"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory, name="skill_category_enum", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    proficiency_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped[User] = relationship("User", back_populates="skills")

    __table_args__ = (
        Index("ix_skills_user_id", "user_id"),
        Index("ix_skills_skill_name", "skill_name"),
    )
