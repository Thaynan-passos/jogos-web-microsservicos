SET ROLE rank_service;

CREATE TABLE ranking_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL UNIQUE,
    user_id UUID NOT NULL,
    game_slug VARCHAR(50) NOT NULL CHECK (game_slug ~ '^[a-z0-9-]+$'),
    score INTEGER NOT NULL CHECK (score >= 0),
    duration_ms INTEGER CHECK (duration_ms IS NULL OR duration_ms >= 0),
    achieved_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ranking_entries_leaderboard_idx
    ON ranking_entries (game_slug, score DESC, achieved_at ASC);
CREATE INDEX ranking_entries_user_game_idx
    ON ranking_entries (user_id, game_slug);
