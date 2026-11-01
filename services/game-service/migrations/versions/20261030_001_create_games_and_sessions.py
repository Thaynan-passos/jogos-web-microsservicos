"""create games and game sessions

Revision ID: 20261030_001
Revises:
Create Date: 2026-10-30

"""

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects import postgresql

revision = "20261030_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = None if context.is_offline_mode() else sa.inspect(bind)

    if inspector is None or not inspector.has_table("games"):
        op.create_table(
            "games",
            sa.Column("slug", sa.String(length=50), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column(
                "description",
                sa.Text(),
                server_default=sa.text("''"),
                nullable=False,
            ),
            sa.Column(
                "enabled",
                sa.Boolean(),
                server_default=sa.true(),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("slug"),
            sa.CheckConstraint("slug ~ '^[a-z0-9-]+$'", name="games_slug_format"),
        )

    if inspector is None or not inspector.has_table("game_sessions"):
        op.create_table(
            "game_sessions",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("game_slug", sa.String(length=50), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column(
                "status",
                sa.String(length=20),
                server_default=sa.text("'in_progress'"),
                nullable=False,
            ),
            sa.Column(
                "result",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
            sa.Column(
                "started_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["game_slug"], ["games.slug"]),
            sa.PrimaryKeyConstraint("id"),
            sa.CheckConstraint(
                "status IN ('in_progress', 'completed', 'abandoned')",
                name="game_sessions_status_values",
            ),
            sa.CheckConstraint(
                "status <> 'completed' OR completed_at IS NOT NULL",
                name="game_sessions_completed_at",
            ),
        )

    existing_indexes = set()
    if inspector is not None:
        inspector = sa.inspect(bind)
        existing_indexes = {
            index["name"] for index in inspector.get_indexes("game_sessions")
        }
    if "game_sessions_user_id_idx" not in existing_indexes:
        op.create_index("game_sessions_user_id_idx", "game_sessions", ["user_id"])
    if "game_sessions_game_started_idx" not in existing_indexes:
        op.create_index(
            "game_sessions_game_started_idx",
            "game_sessions",
            ["game_slug", sa.text("started_at DESC")],
        )

    op.execute(
        sa.text(
            """
            INSERT INTO games (slug, name, description)
            VALUES
                ('jogo-da-velha', 'Jogo da Velha', 'Clássico jogo para dois jogadores.'),
                ('jogo-da-memoria', 'Jogo da Memória', 'Encontre os pares de cartas iguais.'),
                ('pedra-papel-tesoura', 'Pedra, Papel e Tesoura', 'Desafie o computador.')
            ON CONFLICT (slug) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.drop_index("game_sessions_game_started_idx", table_name="game_sessions")
    op.drop_index("game_sessions_user_id_idx", table_name="game_sessions")
    op.drop_table("game_sessions")
    op.drop_table("games")
