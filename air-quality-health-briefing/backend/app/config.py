from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="forbid")

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    OPENAQ_API_KEY: str
    OPENROUTER_API_KEY: str
    BREVO_API_KEY: str

    APP_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    DEBUG: bool = False
    DAILY_AI_QUOTA: int = 50

    FROM_EMAIL: str = "briefings@yourdomain.com"
    FROM_NAME: str = "AirBrief"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
