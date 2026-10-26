SET ROLE user_service;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL CHECK (length(trim(name)) BETWEEN 2 AND 100),
    username VARCHAR(30) NOT NULL CHECK (username ~ '^[a-zA-Z0-9_]{3,30}$'),
    email VARCHAR(320) NOT NULL,
    password_hash TEXT NOT NULL CHECK (length(password_hash) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX users_username_lower_unique ON users (lower(username));
CREATE UNIQUE INDEX users_email_lower_unique ON users (lower(email));
