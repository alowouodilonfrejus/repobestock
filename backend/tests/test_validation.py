import uuid

from tests.test_equipements import _referentiels, _payload


async def test_equipement_nom_too_long(client, auth_headers):
    cats, statuts, empls = await _referentiels(client, auth_headers)
    payload = _payload(cats[0]["id"], statuts[0]["id"], empls[0]["id"])
    payload["nom"] = "X" * 151
    resp = await client.post("/api/v1/equipements", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_equipement_reference_too_long(client, auth_headers):
    cats, statuts, empls = await _referentiels(client, auth_headers)
    payload = _payload(cats[0]["id"], statuts[0]["id"], empls[0]["id"])
    payload["reference"] = "X" * 51
    resp = await client.post("/api/v1/equipements", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_equipements_limit_cap(client, auth_headers):
    resp = await client.get("/api/v1/equipements?limit=501", headers=auth_headers)
    assert resp.status_code == 422


async def test_equipements_negative_skip(client, auth_headers):
    resp = await client.get("/api/v1/equipements?skip=-1", headers=auth_headers)
    assert resp.status_code == 422


async def test_categories_empty_nom_not_tested(client, auth_headers):
    resp = await client.get("/api/v1/categories", headers=auth_headers)
    assert resp.status_code == 200
    assert all(c["actif"] is True for c in resp.json())