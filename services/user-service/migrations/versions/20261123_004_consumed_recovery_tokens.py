"""persist consumed password recovery tokens

Revision ID: 20261123_004
Revises: 20261119_003
Create Date: 2026-11-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261123_004"
down_revision: str | Sequence[str] | None = "20261119_003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "consumed_recovery_tokens",
        sa.Column("token_id", sa.String(length=36), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("token_id"),
    )


def downgrade() -> None:
    op.drop_table("consumed_recovery_tokens")
