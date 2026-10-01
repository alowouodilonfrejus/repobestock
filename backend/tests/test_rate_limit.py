"""Rate limiting : partage inter-workers, anti-spoofing X-Forwarded-For."""

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.middleware import rate_limit as rl


async def _login(request):
    return JSONResponse({"ok": True})


@pytest.fixture
def store_file(tmp_path, monkeypatch):
    path = tmp_path / "ratelimit.json"
    monkeypatch.setattr(rl, "STORE_PATH", path)
    # Chaque test repart d'un magasin vide
    monkeypatch.setattr(rl, "_store", rl._FileStore())
    return path


def _client() -> TestClient:
    app = Starlette(routes=[Route("/api/v1/auth/login", _login, methods=["POST"])])
    rl.setup_rate_limiting(app)
    return TestClient(app)


def test_limit_is_applied(store_file):
    client = _client()
    for _ in range(5):
        assert client.post("/api/v1/auth/login").status_code == 200
    assert client.post("/api/v1/auth/login").status_code == 429


def test_counter_is_shared_across_instances(store_file):
    """Deux middleware (= deux workers uvicorn) voient le meme compteur."""
    for _ in range(5):
        assert _client().post("/api/v1/auth/login").status_code == 200
    assert _client().post("/api/v1/auth/login").status_code == 429


def test_xff_is_ignored_without_trust_proxy(store_file, monkeypatch):
    monkeypatch.setattr(rl, "TRUST_PROXY", False)
    client = _client()
    for i in range(5):
        resp = client.post(
            "/api/v1/auth/login", headers={"X-Forwarded-For": f"10.0.0.{i}"}
        )
        assert resp.status_code == 200
    # IP falsifiees differentes : sans TRUST_PROXY, une seule budget est compte
    resp = client.post(
        "/api/v1/auth/login", headers={"X-Forwarded-For": "10.0.0.99"}
    )
    assert resp.status_code == 429


def test_xff_honored_with_trust_proxy(store_file, monkeypatch):
    monkeypatch.setattr(rl, "TRUST_PROXY", True)
    client = _client()
    for i in range(5):
        resp = client.post(
            "/api/v1/auth/login", headers={"X-Forwarded-For": f"10.0.0.{i}"}
        )
        assert resp.status_code == 200
    # Chaque IP forwardsed a son propre budget
    resp = client.post(
        "/api/v1/auth/login", headers={"X-Forwarded-For": "10.0.0.99"}
    )
    assert resp.status_code == 200


def test_store_file_stays_small(store_file):
    client = _client()
    for _ in range(3):
        client.post("/api/v1/auth/login")
    assert store_file.exists()
    data = store_file.read_text(encoding="utf-8")
    assert len(data) < 1000
