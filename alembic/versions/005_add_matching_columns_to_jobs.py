"""add matching columns to jobs

Revision ID: 005
Revises: 004
Create Date: 2026-03-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("match_level", sa.String(20), nullable=True))
    op.add_column("jobs", sa.Column("match_reason", sa.Text(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.add_column("jobs", sa.Column("extracted_yoe", sa.Integer(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column(
            "extracted_skills",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("extracted_education", sa.Text(), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("raw_description_hash", sa.String(64), nullable=True),
    )

    op.create_index("ix_jobs_match_level", "jobs", ["match_level"])
    op.create_index("ix_jobs_description_hash", "jobs", ["raw_description_hash"])
    op.create_index("ix_jobs_is_active", "jobs", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_jobs_is_active", table_name="jobs")
    op.drop_index("ix_jobs_description_hash", table_name="jobs")
    op.drop_index("ix_jobs_match_level", table_name="jobs")

    op.drop_column("jobs", "raw_description_hash")
    op.drop_column("jobs", "extracted_education")
    op.drop_column("jobs", "extracted_skills")
    op.drop_column("jobs", "extracted_yoe")
    op.drop_column("jobs", "is_active")
    op.drop_column("jobs", "matched_at")
    op.drop_column("jobs", "match_reason")
    op.drop_column("jobs", "match_level")
