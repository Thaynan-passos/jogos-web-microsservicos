from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Password Recovery Service"
    ENVIRONMENT: str = "production"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    RECOVERY_TOKEN_SECRET_KEY: str
    USER_SERVICE_SHARED_SECRET: str = Field(
        validation_alias=AliasChoices(
            "USER_SERVICE_SHARED_SECRET", "RECOVERY_SERVICE_SECRET"
        )
    )
    ALGORITHM: str = "HS256"
    RECOVERY_TOKEN_EXPIRE_MINUTES: int = 15
    USER_SERVICE_URL: str = "http://user-service:8000"
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None


settings = Settings()
