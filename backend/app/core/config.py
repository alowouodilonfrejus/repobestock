import os
import warnings
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> Path:
    """Resout env/.env de facon robuste (dev local + Docker WORKDIR /app)."""
    if env_file := os.getenv("ENV_FILE"):
        return Path(env_file)
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / "env" / ".env",  # bestock-main/env/.env (dev local)
        here.parents[2] / "env" / ".env",  # backend/env/.env fallback
        Path("/app/env/.env"),  # Docker si env monte a /app
        Path.cwd() / "env" / ".env",
        Path.cwd().parent / "env" / ".env",
    ]
    for p in candidates:
        if p.is_file():
            return p
    # Fallback historique (meme si inexistant, Pydantic l'ignore silencieusement)
    return here.parents[3] / "env" / ".env"


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = _resolve_env_file()

_PRODUCTION_VALUES = {"production", "prod"}


def is_production() -> bool:
    """Detecte un deploiement production, quel que soit le fournisseur.

    Couvre le drapeur classique ENV/ENVIRONMENT/APP_ENV ainsi que les
    variables injectees automatiquement par Railway, Render et Vercel,
    afin que les gardes-fous secrets ne dependent plus d'un seul flag.
    """
    flags = (
        "ENV",
        "ENVIRONMENT",
        "APP_ENV",
        "RAILWAY_ENVIRONMENT",
        "RAILWAY_PROJECT_ENVIRONMENT",
        "RENDER",
        "VERCEL_ENV",
    )
    return any(
        (os.getenv(flag) or "").strip().lower() in _PRODUCTION_VALUES
        for flag in flags
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore"
    )

    PROJECT_NAME: str = "BeStock API"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bestock_db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _coerce_database_url(cls, v: str) -> str:
        # Railway fournit DATABASE_URL en postgres:// ou postgresql://
        # SQLAlchemy asyncpg exige postgresql+asyncpg://
        if isinstance(v, str):
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            # Railway ajoute parfois ?sslmode=require — asyncpg le supporte
        return v
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FIRST_SUPERUSER_EMAIL: str = "admin@bestock.dev"
    FIRST_SUPERUSER_PASSWORD: str = "admin1234"
    FIRST_SUPERUSER_USERNAME: str = "superadmin"

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator("SECRET_KEY")
    @classmethod
    def _check_secret_key(cls, v: str) -> str:
        # En production on exige une cle forte ; en dev on avertit seulement
        if v == "change-me-in-production" or v.startswith("REPLACE_ME"):
            if is_production():
                raise ValueError(
                    "SECRET_KEY doit etre defini via variable d'environnement en production "
                    "(min 32 caracteres, genere avec: python -c 'import secrets; print(secrets.token_urlsafe(32))')"
                )
            warnings.warn(
                "SECRET_KEY utilise la valeur par defaut 'change-me-in-production' — "
                "ne jamais utiliser en production",
                UserWarning,
                stacklevel=2,
            )
        elif len(v) < 32:
            raise ValueError("SECRET_KEY doit contenir au moins 32 caracteres")
        return v

    @field_validator("ALGORITHM")
    @classmethod
    def _check_algorithm(cls, v: str) -> str:
        allowed = {"HS256", "HS384", "HS512"}
        if v not in allowed:
            raise ValueError(f"ALGORITHM doit etre l'un de {allowed}")
        return v

    @field_validator("FIRST_SUPERUSER_PASSWORD")
    @classmethod
    def _check_superuser_password(cls, v: str) -> str:
        if v == "admin1234" and is_production():
            raise ValueError("FIRST_SUPERUSER_PASSWORD par defaut 'admin1234' interdit en production")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
