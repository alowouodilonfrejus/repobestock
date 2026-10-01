"""Tests hors-ligne de la couche securite (JWT, bcrypt, refresh tokens)."""

from datetime import datetime, timedelta, timezone

import bcrypt
import pytest

from app.core.security import (
    MAX_PASSWORD_BYTES,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


class TestPasswords:
    def test_hash_and_verify(self):
        hashed = hash_password("Secret123!")
        assert hashed != "Secret123!"
        assert verify_password("Secret123!", hashed)
        assert not verify_password("mauvais", hashed)

    def test_hash_is_salted(self):
        assert hash_password("Secret123!") != hash_password("Secret123!")

    def test_too_long_password_rejected(self):
        long_pwd = "a" * (MAX_PASSWORD_BYTES + 1)
        with pytest.raises(ValueError, match="trop long"):
            hash_password(long_pwd)

    def test_too_long_plain_never_verifies(self):
        # bcrypt tronque a 72 octets : on refuse plutot que comparer tronque
        hashed = hash_password("a" * MAX_PASSWORD_BYTES)
        assert not verify_password("a" * (MAX_PASSWORD_BYTES + 1), hashed)

    def test_verify_with_corrupted_hash(self):
        assert not verify_password("Secret123!", "pas-un-hash")


class TestAccessToken:
    def test_roundtrip(self):
        token = create_access_token("42")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_expired_token_rejected(self):
        token = create_access_token("42", expires_delta=timedelta(seconds=-5))
        assert decode_access_token(token) is None

    def test_tampered_signature_rejected(self):
        token = create_access_token("42")
        forged = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
        assert decode_access_token(forged) is None

    def test_wrong_type_rejected(self):
        import jwt

        from app.core.config import settings

        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {"sub": "1", "iat": now, "exp": now + timedelta(minutes=5), "type": "refresh"},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        assert decode_access_token(token) is None


class TestRefreshToken:
    def test_generated_token_is_long_and_unique(self):
        a, b = generate_refresh_token(), generate_refresh_token()
        assert a != b
        assert len(a) >= 48

    def test_hash_is_sha256_hex_and_not_reversible(self):
        token = generate_refresh_token()
        digest = hash_refresh_token(token)
        assert len(digest) == 64
        assert digest != token
        assert digest == hash_refresh_token(token)

    def test_bcrypt_limit_constant(self):
        assert MAX_PASSWORD_BYTES == 72
        assert isinstance(bcrypt.__version__, str)
