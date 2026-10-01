"""Demarrage hors-ligne de l'application : import + middlewares + sante."""

from starlette.testclient import TestClient

from app.main import app


def test_app_imports_without_database():
    assert app.title == "BeStock API"


def test_health_endpoint():
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_security_headers_present():
    with TestClient(app) as client:
        resp = client.get("/health")
    assert "x-content-type-options" in resp.headers
    assert "x-frame-options" in resp.headers


def test_openapi_available():
    with TestClient(app) as client:
        resp = client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    assert "/api/v1/auth/login/json" in resp.json()["paths"]
