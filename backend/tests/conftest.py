"""Fixtures : client HTTP authentifie contre l'API live (Docker).

Cache le token pour eviter le rate limiting (5 login/min).
Les tests live sont sautes si l'API n'est pas lancee.
"""

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"
_cached_token: str | None = None
_reachable: bool | None = None


async def _api_reachable() -> bool:
    global _reachable
    if _reachable is None:
        try:
            async with AsyncClient(base_url=BASE_URL, timeout=2.0) as probe:
                resp = await probe.get("/health")
                _reachable = resp.status_code == 200
        except httpx.HTTPError:
            _reachable = False
    return _reachable


async def _get_token() -> str:
    global _cached_token
    if _cached_token is not None:
        return _cached_token
    async with AsyncClient(base_url=BASE_URL) as tmp:
        login = await tmp.post(
            "/api/v1/auth/login/json",
            json={"email": "admin@bestock.dev", "password": "admin1234"},
        )
        assert login.status_code == 200, f"Login echoue : {login.text}"
        _cached_token = login.json()["access_token"]
        return _cached_token


@pytest_asyncio.fixture
async def client():
    if not await _api_reachable():
        pytest.skip("API live indisponible sur localhost:8000 (docker compose up)")
    token = await _get_token()
    async with AsyncClient(base_url=BASE_URL) as c:
        c.headers["Authorization"] = f"Bearer {token}"
        yield c
