async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_openapi_available(client):
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    body = resp.json()
    assert body["info"]["title"] == "BeStock API"
    assert "/api/v1/auth/login/json" in body["paths"]


async def test_unknown_route(client):
    resp = await client.get("/api/v1/inexistant")
    assert resp.status_code == 404