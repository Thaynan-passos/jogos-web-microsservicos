from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Password Recovery Service"
    SECRET_KEY: str = "recovery-service-default-secret-key-32-chars-min"
    ALGORITHM: str = "HS256"
    RECOVERY_TOKEN_EXPIRE_MINUTES: int = 15
    USER_SERVICE_URL: str = "http://user-service:8000"


settings = Settings()
