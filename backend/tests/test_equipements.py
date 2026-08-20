import uuid


def _unique_ref():
    return f"REF-{uuid.uuid4().hex[:8].upper()}"


async def _referentiels(client, auth_headers):
    cats = (await client.get("/api/v1/categories", headers=auth_headers)).json()
    statuts = (await client.get("/api/v1/statuts", headers=auth_headers)).json()
    empls = (await client.get("/api/v1/emplacements", headers=auth_headers)).json()
    return cats, statuts, empls


def _payload(categorie_id, statut_id, emplacement_id):
    return {
        "reference": _unique_ref(),
        "nom": "Serveur Dell PowerEdge",
        "description": "Equipement de test",
        "marque": "Dell",
        "modele": "PowerEdge R750",
        "numero_serie": f"SN-{uuid.uuid4().hex[:8].upper()}",
        "date_acquisition": "2026-01-15",
        "categorie_id": categorie_id,
        "statut_id": statut_id,
        "emplacement_id": emplacement_id,
    }


async def test_create_get_update_delete_flow(client, auth_headers):
    cats, statuts, empls = await _referentiels(client, auth_headers)
    payload = _payload(cats[0]["id"], statuts[0]["id"], empls[0]["id"])

    created = await client.post("/api/v1/equipements", json=payload, headers=auth_headers)
    assert created.status_code == 201, created.text
    body = created.json()
    eq_id = body["id"]
    assert body["nom"] == payload["nom"]

    fetched = await client.get(f"/api/v1/equipements/{eq_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["reference"] == payload["reference"]

    updated = await client.put(
        f"/api/v1/equipements/{eq_id}",
        json={"nom": "Serveur Dell PowerEdge XE"},
        headers=auth_headers,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["nom"] == "Serveur Dell PowerEdge XE"

    historique = await client.get(
        f"/api/v1/equipements/{eq_id}/historique", headers=auth_headers
    )
    assert historique.status_code == 200
    actions = [h["action"] for h in historique.json()]
    assert "creation" in actions
    assert "modification" in actions

    deleted = await client.delete(f"/api/v1/equipements/{eq_id}", headers=auth_headers)
    assert deleted.status_code == 204

    gone = await client.get(f"/api/v1/equipements/{eq_id}", headers=auth_headers)
    assert gone.status_code == 404


async def test_duplicate_reference_conflict(client, auth_headers):
    cats, statuts, empls = await _referentiels(client, auth_headers)
    payload = _payload(cats[0]["id"], statuts[0]["id"], empls[0]["id"])

    first = await client.post("/api/v1/equipements", json=payload, headers=auth_headers)
    assert first.status_code == 201

    payload["nom"] = "Un autre nom"
    second = await client.post("/api/v1/equipements", json=payload, headers=auth_headers)
    assert second.status_code == 409


async def test_stats_endpoint(client, auth_headers):
    cats, statuts, empls = await _referentiels(client, auth_headers)
    payload = _payload(cats[0]["id"], statuts[0]["id"], empls[0]["id"])
    await client.post("/api/v1/equipements", json=payload, headers=auth_headers)

    resp = await client.get("/api/v1/equipements/stats", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total"] >= 1
    assert "maintenance" in body
    assert isinstance(body["recent"], list)


async def test_equipement_not_found(client, auth_headers):
    resp = await client.get("/api/v1/equipements/999999", headers=auth_headers)
    assert resp.status_code == 404


async def test_create_with_bad_fk(client, auth_headers):
    cats, statuts, empls = await _referentiels(client, auth_headers)
    payload = _payload(999999, statuts[0]["id"], empls[0]["id"])
    resp = await client.post("/api/v1/equipements", json=payload, headers=auth_headers)
    assert resp.status_code == 400