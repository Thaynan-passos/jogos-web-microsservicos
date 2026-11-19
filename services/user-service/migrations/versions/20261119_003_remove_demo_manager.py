"""remove the manager account created with a published fixed password

Revision ID: 20261119_003
Revises: 20261103_002
Create Date: 2026-11-19

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261119_003"
down_revision: str | Sequence[str] | None = "20261103_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM users "
            "WHERE username = :username AND email = :email AND is_admin = true"
        ).bindparams(username="Gerente", email="Gerente@playground.com")
    )


def downgrade() -> None:
    # Do not recreate an account with a fixed or published credential.
    pass
