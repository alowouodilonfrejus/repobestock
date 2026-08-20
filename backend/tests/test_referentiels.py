async def test_categories(client, auth_headers):
    resp = await client.get("/api/v1/categories", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) >= 3
    noms = [c["nom"] for c in data]
    assert "Informatique" in noms
    assert "Immobilier" in noms


async def test_statuts(client, auth_headers):
    resp = await client.get("/api/v1/statuts", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    noms = [s["nom"] for s in resp.json()]
    assert "Fonctionnel" in noms
    assert "En maintenance" in noms


async def test_emplacements(client, auth_headers):
    resp = await client.get("/api/v1/emplacements", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    noms = [e["nom"] for e in resp.json()]
    assert "Entrepot" in noms
    assert "Bureau" in noms


async def test_equipements_list_shape(client, auth_headers):
    resp = await client.get("/api/v1/equipements", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "items" in body and "total" in body
    assert body["limit"] == 100
    assert isinstance(body["items"], list)


async def test_historique_global(client, auth_headers):
    resp = await client.get("/api/v1/historique", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


async def test_users_list(client, auth_headers):
    resp = await client.get("/api/v1/users", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "items" in body
    assert any(u["role"] == "superadmin" for u in body["items"])