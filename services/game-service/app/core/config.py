from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Game Service"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    USER_SERVICE_URL: str = "http://user-service:8000"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
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
