from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    PROJECT_NAME: str = "BeStock API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bestock_db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    FIRST_SUPERUSER_EMAIL: str = "admin@bestock.dev"
    FIRST_SUPERUSER_PASSWORD: str = "admin1234"
    FIRST_SUPERUSER_USERNAME: str = "superadmin"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
