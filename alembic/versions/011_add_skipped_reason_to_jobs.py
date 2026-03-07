"""add skipped_reason to jobs

Revision ID: 011
Revises: 010
Create Date: 2026-03-06

- Add skipped_reason VARCHAR(50) nullable for gate filtering (salary_gate, critical_skills_gate, etc.)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("skipped_reason", sa.String(50), nullable=True),
    )
    op.create_index("ix_jobs_skipped_reason", "jobs", ["skipped_reason"])


def downgrade() -> None:
    op.drop_index("ix_jobs_skipped_reason", table_name="jobs")
    op.drop_column("jobs", "skipped_reason")
