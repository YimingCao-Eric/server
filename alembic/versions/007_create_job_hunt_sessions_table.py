"""create job_hunt_sessions table

Revision ID: 007
Revises: 006
Create Date: 2026-03-03
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_hunt_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column(
            "search_keywords",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'::text[]"),
            nullable=True,
        ),
        sa.Column(
            "search_locations",
            postgresql.ARRAY(sa.Text()),
            server_default=sa.text("'{}'::text[]"),
            nullable=True,
        ),
        sa.Column(
            "jobs_scraped",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "jobs_filtered",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "jobs_matched",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "jobs_applied",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_job_hunt_sessions")),
    )
    op.create_index(
        "ix_job_hunt_sessions_user_id",
        "job_hunt_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_job_hunt_sessions_session_date",
        "job_hunt_sessions",
        ["session_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_job_hunt_sessions_session_date",
        table_name="job_hunt_sessions",
    )
    op.drop_index(
        "ix_job_hunt_sessions_user_id",
        table_name="job_hunt_sessions",
    )
    op.drop_table("job_hunt_sessions")
