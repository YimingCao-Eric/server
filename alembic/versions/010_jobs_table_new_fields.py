"""jobs table new fields (migration 010)

Revision ID: 010
Revises: 009
Create Date: 2026-03-06

- Rename source_url -> job_url
- Add apply_url, easy_apply, external_id, dismissed, job_type, remote_type, etc.
- Change extracted_yoe from INTEGER to FLOAT
- Add indexes: ix_jobs_dismissed, ix_jobs_external_id, ix_jobs_raw_description_hash
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename source_url -> job_url
    op.alter_column(
        "jobs",
        "source_url",
        new_column_name="job_url",
        existing_type=sa.Text(),
        existing_nullable=True,
    )

    # Rename the unique index for consistency
    op.execute("ALTER INDEX ix_jobs_source_url RENAME TO ix_jobs_job_url")

    # 2. Add new columns
    op.add_column("jobs", sa.Column("apply_url", sa.String(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("easy_apply", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("jobs", sa.Column("external_id", sa.String(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("dismissed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("jobs", sa.Column("job_type", sa.String(20), nullable=True))
    op.add_column("jobs", sa.Column("remote_type", sa.String(20), nullable=True))
    op.add_column("jobs", sa.Column("seniority_level", sa.String(20), nullable=True))
    op.add_column("jobs", sa.Column("industry", sa.String(50), nullable=True))
    op.add_column("jobs", sa.Column("visa_sponsorship_required", sa.Boolean(), nullable=True))
    op.add_column("jobs", sa.Column("salary_min", sa.Float(), nullable=True))
    op.add_column("jobs", sa.Column("salary_max", sa.Float(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("required_skills", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("nice_to_have_skills", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("critical_skills", postgresql.JSONB(), nullable=True),
    )
    op.add_column("jobs", sa.Column("education_field", sa.String(50), nullable=True))
    op.add_column("jobs", sa.Column("confidence", sa.String(10), nullable=True))
    op.add_column("jobs", sa.Column("fit_score", sa.Float(), nullable=True))
    op.add_column("jobs", sa.Column("req_coverage", sa.Float(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("jd_incomplete", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "jobs",
        sa.Column("recurring_unapplied", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # 3. Change extracted_yoe from INTEGER to FLOAT
    op.alter_column(
        "jobs",
        "extracted_yoe",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=True,
        postgresql_using="extracted_yoe::float",
    )

    # 4. Drop old index and create ix_jobs_raw_description_hash (migration 005 had ix_jobs_description_hash)
    op.drop_index("ix_jobs_description_hash", table_name="jobs")
    op.create_index("ix_jobs_raw_description_hash", "jobs", ["raw_description_hash"])

    # 5. Add new indexes
    op.create_index("ix_jobs_dismissed", "jobs", ["dismissed"])
    op.create_index("ix_jobs_external_id", "jobs", ["external_id"])


def downgrade() -> None:
    op.drop_index("ix_jobs_external_id", table_name="jobs")
    op.drop_index("ix_jobs_dismissed", table_name="jobs")
    op.drop_index("ix_jobs_raw_description_hash", table_name="jobs")
    op.create_index("ix_jobs_description_hash", "jobs", ["raw_description_hash"])

    op.alter_column(
        "jobs",
        "extracted_yoe",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="extracted_yoe::integer",
    )

    op.drop_column("jobs", "recurring_unapplied")
    op.drop_column("jobs", "jd_incomplete")
    op.drop_column("jobs", "req_coverage")
    op.drop_column("jobs", "fit_score")
    op.drop_column("jobs", "confidence")
    op.drop_column("jobs", "education_field")
    op.drop_column("jobs", "critical_skills")
    op.drop_column("jobs", "nice_to_have_skills")
    op.drop_column("jobs", "required_skills")
    op.drop_column("jobs", "salary_max")
    op.drop_column("jobs", "salary_min")
    op.drop_column("jobs", "visa_sponsorship_required")
    op.drop_column("jobs", "industry")
    op.drop_column("jobs", "seniority_level")
    op.drop_column("jobs", "remote_type")
    op.drop_column("jobs", "job_type")
    op.drop_column("jobs", "dismissed")
    op.drop_column("jobs", "external_id")
    op.drop_column("jobs", "easy_apply")
    op.drop_column("jobs", "apply_url")

    op.execute("ALTER INDEX ix_jobs_job_url RENAME TO ix_jobs_source_url")
    op.alter_column(
        "jobs",
        "job_url",
        new_column_name="source_url",
        existing_type=sa.Text(),
        existing_nullable=True,
    )
