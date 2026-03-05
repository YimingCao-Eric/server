"""fix extracted_education column type to varchar20

Revision ID: 009
Revises: 008
Create Date: 2026-03-04

"""
from typing import Sequence, Union

from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE jobs ALTER COLUMN extracted_education TYPE VARCHAR(20)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE jobs ALTER COLUMN extracted_education TYPE TEXT")
