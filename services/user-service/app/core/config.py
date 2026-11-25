from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_async_database_url(database_url: str) -> str:
    """Normaliza URLs PostgreSQL (ex.: Neon) para uso com SQLAlchemy + asyncpg."""
    parsed = urlsplit(database_url.strip())
    scheme = (
        "postgresql+asyncpg"
        if parsed.scheme in {"postgres", "postgresql"}
        else parsed.scheme
    )
    query_params: list[tuple[str, str]] = []
    has_ssl = False
    ssl_required = False
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key == "channel_binding":
            continue
        if key == "sslmode":
            if value in {"require", "verify-ca", "verify-full"}:
                ssl_required = True
            continue
        if key == "ssl":
            has_ssl = True
        query_params.append((key, value))
    if ssl_required and not has_ssl:
        query_params.append(("ssl", "require"))
    return urlunsplit(
        (scheme, parsed.netloc, parsed.path, urlencode(query_params), parsed.fragment)
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "User Service"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    # Jwt
    JWT_SECRET_KEY: str
    RECOVERY_SERVICE_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        if self.DATABASE_URL:
            return normalize_async_database_url(self.DATABASE_URL)
        if not self.POSTGRES_USER or not self.POSTGRES_PASSWORD or not self.POSTGRES_DB:
            raise ValueError(
                "Configure DATABASE_URL ou POSTGRES_USER, POSTGRES_PASSWORD e POSTGRES_DB"
            )
        return str(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


settings = Settings()  # pyright: ignore[reportCallIssue]
