"""create jobs table

Revision ID: 003
Revises: 002
Create Date: 2026-02-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("website", sa.String(50), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("job_description", sa.Text, nullable=False),
        sa.Column("post_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("search_keyword", sa.String(255), nullable=True),
        sa.Column("search_location", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
    )

    op.create_index("ix_jobs_website", "jobs", ["website"])
    op.create_index("ix_jobs_job_title", "jobs", ["job_title"])
    op.create_index("ix_jobs_company", "jobs", ["company"])
    op.create_index(
        "ix_jobs_source_url",
        "jobs",
        ["source_url"],
        unique=True,
        postgresql_where=sa.text("source_url IS NOT NULL"),
    )
    op.create_index("ix_jobs_dedup", "jobs", ["website", "job_title", "company"])


def downgrade() -> None:
    op.drop_index("ix_jobs_dedup", table_name="jobs")
    op.drop_index("ix_jobs_source_url", table_name="jobs")
    op.drop_index("ix_jobs_company", table_name="jobs")
    op.drop_index("ix_jobs_job_title", table_name="jobs")
    op.drop_index("ix_jobs_website", table_name="jobs")
    op.drop_table("jobs")
