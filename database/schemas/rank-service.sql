SET ROLE rank_service;

CREATE TABLE rank_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL,
    game_slug VARCHAR(50) NOT NULL CHECK (game_slug ~ '^[a-z0-9-]+$'),
    score INTEGER NOT NULL CHECK (score >= 0),
    duration_ms INTEGER NOT NULL DEFAULT 0 CHECK (duration_ms >= 0),
    achieved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    matches_played INTEGER NOT NULL DEFAULT 1 CHECK (matches_played > 0),
    win_rate VARCHAR(10) NOT NULL DEFAULT '100%'
);

CREATE UNIQUE INDEX uq_rank_user_game
    ON rank_entries (lower(username), game_slug);

CREATE INDEX rank_entries_leaderboard_idx
    ON rank_entries (game_slug, score DESC, duration_ms ASC);
CREATE INDEX rank_entries_user_game_idx
    ON rank_entries (user_id, game_slug);
