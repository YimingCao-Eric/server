"""create job_applications table

Revision ID: 006
Revises: 005
Create Date: 2026-03-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_applications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("job_title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("apply_url", sa.Text(), nullable=False),
        sa.Column("date_year", sa.Integer(), nullable=False),
        sa.Column("date_month", sa.Integer(), nullable=False),
        sa.Column("date_day", sa.Integer(), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column(
            "yoe",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "skill_set",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
        sa.Column(
            "interview",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "offer",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "rejected",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_applications")),
        sa.UniqueConstraint(
            "apply_url",
            name="uq_job_applications_apply_url",
        ),
        sa.CheckConstraint(
            "date_month BETWEEN 1 AND 12",
            name="ck_job_applications_date_month",
        ),
        sa.CheckConstraint(
            "date_day BETWEEN 1 AND 31",
            name="ck_job_applications_date_day",
        ),
    )
    op.create_index(
        "ix_job_applications_interview",
        "job_applications",
        ["interview"],
    )
    op.create_index(
        "ix_job_applications_offer",
        "job_applications",
        ["offer"],
    )
    op.create_index(
        "ix_job_applications_rejected",
        "job_applications",
        ["rejected"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_job_applications_rejected",
        table_name="job_applications",
    )
    op.drop_index(
        "ix_job_applications_offer",
        table_name="job_applications",
    )
    op.drop_index(
        "ix_job_applications_interview",
        table_name="job_applications",
    )
    op.drop_table("job_applications")
