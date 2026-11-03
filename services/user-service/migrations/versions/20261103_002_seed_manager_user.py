"""seed local manager user

Revision ID: 20261103_002
Revises: 04181db34194
Create Date: 2026-11-03

"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "20261103_002"
down_revision: str | Sequence[str] | None = "04181db34194"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MANAGER_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
MANAGER_USERNAME = "Gerente"
MANAGER_EMAIL = "Gerente@playground.com"
MANAGER_PASSWORD_HASH = "$2b$12$56ovIq3JmcKVIqCdL.NUjeRPXf92RD79RYXJ2mCic6wPMFwi037fW"
CREATED_AT = datetime.now(UTC)


def upgrade() -> None:
    users = sa.table(
        "users",
        sa.column("id", sa.UUID()),
        sa.column("username", sa.String()),
        sa.column("email", sa.String()),
        sa.column("hashed_password", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("is_admin", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        users,
        [
            {
                "id": MANAGER_ID,
                "username": MANAGER_USERNAME,
                "email": MANAGER_EMAIL,
                "hashed_password": MANAGER_PASSWORD_HASH,
                "is_active": True,
                "is_admin": True,
                "created_at": CREATED_AT,
                "updated_at": CREATED_AT,
            }
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM users WHERE id = :manager_id").bindparams(
            manager_id=MANAGER_ID
        )
    )
