"""Fixtures : client HTTP authentifie contre l'API live (Docker).

Cache le token pour eviter le rate limiting (5 login/min).
"""

import pytest_asyncio
from httpx import AsyncClient

_cached_token: str | None = None


async def _get_token() -> str:
    global _cached_token
    if _cached_token is not None:
        return _cached_token
    async with AsyncClient(base_url="http://localhost:8000") as tmp:
        login = await tmp.post(
            "/api/v1/auth/login/json",
            json={"email": "admin@bestock.dev", "password": "admin1234"},
        )
        assert login.status_code == 200, f"Login echoue : {login.text}"
        _cached_token = login.json()["access_token"]
        return _cached_token


@pytest_asyncio.fixture
async def client():
    token = await _get_token()
    async with AsyncClient(base_url="http://localhost:8000") as c:
        c.headers["Authorization"] = f"Bearer {token}"
        yield c
