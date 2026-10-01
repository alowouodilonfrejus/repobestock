"""Gardes-fous de configuration : jamais de secrets faibles en production."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings

_STRONG_KEY = "x" * 40
_SAFE_PWD = "MotDePasseFort!123"


def _settings(**overrides) -> Settings:
    base = {
        "SECRET_KEY": _STRONG_KEY,
        "FIRST_SUPERUSER_PASSWORD": _SAFE_PWD,
    }
    base.update(overrides)
    return Settings(**base)


def test_production_rejects_default_secret(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(SECRET_KEY="change-me-in-production")


def test_production_rejects_placeholder_secret(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(SECRET_KEY="REPLACE_ME_GENERE_UNE_NOUVELLE_CLE")


def test_railway_flag_triggers_guards(monkeypatch):
    # Le flag du fournisseur suffit, sans ENV=production explicite
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(SECRET_KEY="change-me-in-production")


def test_production_rejects_default_superuser_password(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    with pytest.raises(ValidationError, match="admin1234"):
        _settings(FIRST_SUPERUSER_PASSWORD="admin1234")


def test_short_secret_always_rejected():
    with pytest.raises(ValidationError, match="32"):
        _settings(SECRET_KEY="court")


def test_dev_default_secret_only_warns(monkeypatch):
    for flag in ("ENV", "ENVIRONMENT", "APP_ENV", "RAILWAY_ENVIRONMENT"):
        monkeypatch.delenv(flag, raising=False)
    with pytest.warns(UserWarning, match="change-me-in-production"):
        _settings(SECRET_KEY="change-me-in-production")


def test_production_accepts_strong_config(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    s = _settings()
    assert s.SECRET_KEY == _STRONG_KEY
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
