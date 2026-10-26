SET ROLE game_service;

CREATE TABLE games (
    slug VARCHAR(50) PRIMARY KEY CHECK (slug ~ '^[a-z0-9-]+$'),
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO games (slug, name, description)
VALUES
    ('jogo-da-velha', 'Jogo da Velha', 'Clássico jogo para dois jogadores.'),
    ('jogo-da-memoria', 'Jogo da Memória', 'Encontre os pares de cartas iguais.'),
    ('pedra-papel-tesoura', 'Pedra, Papel e Tesoura', 'Desafie o computador.')
ON CONFLICT (slug) DO NOTHING;

CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_slug VARCHAR(50) NOT NULL REFERENCES games (slug),
    user_id UUID,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'completed', 'abandoned')),
    result JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    CHECK (status <> 'completed' OR completed_at IS NOT NULL)
);

CREATE INDEX game_sessions_user_id_idx ON game_sessions (user_id);
CREATE INDEX game_sessions_game_started_idx ON game_sessions (game_slug, started_at DESC);
