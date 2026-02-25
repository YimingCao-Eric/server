"""create user profile tables

Revision ID: 001
Revises:
Create Date: 2026-02-25

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

skill_category_enum = postgresql.ENUM(
    "language",
    "framework",
    "database",
    "tooling",
    "machine_learning",
    "soft_skill",
    name="skill_category_enum",
    create_type=False,
)


def upgrade() -> None:
    skill_category_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("linkedin_url", sa.Text, nullable=True),
        sa.Column("github_url", sa.Text, nullable=True),
        sa.Column("personal_website", sa.Text, nullable=True),
        sa.Column("location_country", sa.String(100), nullable=True),
        sa.Column("location_province_state", sa.String(100), nullable=True),
        sa.Column("location_city", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"])

    op.create_table(
        "educations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_name", sa.String(255), nullable=False),
        sa.Column("degree", sa.String(255), nullable=False),
        sa.Column("field_of_study", sa.String(255), nullable=False),
        sa.Column("address_country", sa.String(100), nullable=False),
        sa.Column("address_province_state", sa.String(100), nullable=False),
        sa.Column("address_city", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("graduate_date", sa.Date, nullable=False),
        sa.Column("gpa", sa.String(20), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_educations")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_educations_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "graduate_date >= start_date",
            name=op.f("ck_educations_graduate_date_gte_start_date"),
        ),
    )
    op.create_index(op.f("ix_educations_user_id"), "educations", ["user_id"])

    op.create_table(
        "work_experiences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("location_country", sa.String(100), nullable=True),
        sa.Column("location_province_state", sa.String(100), nullable=True),
        sa.Column("location_city", sa.String(100), nullable=True),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_work_experiences")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_work_experiences_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name=op.f("ck_work_experiences_end_date_gte_start_date"),
        ),
    )
    op.create_index(
        op.f("ix_work_experiences_user_id"), "work_experiences", ["user_id"]
    )
    op.create_index(
        op.f("ix_work_experiences_company_name"),
        "work_experiences",
        ["company_name"],
    )

    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("skill_category", skill_category_enum, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_skills")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_skills_user_id_users"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_skills_user_id"), "skills", ["user_id"])
    op.create_index(op.f("ix_skills_skill_name"), "skills", ["skill_name"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_title", sa.String(255), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_projects_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name=op.f("ck_projects_end_date_gte_start_date"),
        ),
    )
    op.create_index(op.f("ix_projects_user_id"), "projects", ["user_id"])


def downgrade() -> None:
    op.drop_table("projects")
    op.drop_table("skills")
    op.drop_table("work_experiences")
    op.drop_table("educations")
    op.drop_table("users")
    skill_category_enum.drop(op.get_bind(), checkfirst=True)
