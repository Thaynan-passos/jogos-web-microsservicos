"""Retired fixed-credential manager seed.

Revision ID: 20261103_002
Revises: 04181db34194
Create Date: 2026-11-03

"""

from collections.abc import Sequence

revision: str = "20261103_002"
down_revision: str | Sequence[str] | None = "04181db34194"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Admin accounts must be provisioned by the operator with a unique password.
    pass


def downgrade() -> None:
    pass
