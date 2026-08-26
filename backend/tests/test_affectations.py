"""Scenarios principaux du module d'affectation."""

import uuid

import pytest
from httpx import AsyncClient


def uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:6].upper()}"


async def create_employe(client: AsyncClient) -> dict:
    matricule = uid("EMP-")
    resp = await client.post(
        "/api/v1/employes",
        json={
            "nom_complet": f"Test {matricule}",
            "matricule": matricule,
            "departement": "IT",
            "fonction": "Testeur",
            "email": f"{matricule.lower()}@test.dev",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_materiel(
    client: AsyncClient, quantite: int = 10, reference: str | None = None
) -> dict:
    ref = reference or uid("REF-")
    resp = await client.post(
        "/api/v1/equipements",
        json={
            "reference": ref,
            "nom": f"Materiel {ref}",
            "quantite": quantite,
            "categorie_id": 1,
            "statut_id": 5,  # En stock
            "etat": "neuf",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_creer_employe(client: AsyncClient):
    employe = await create_employe(client)
    assert employe["matricule"].startswith("EMP-")
    assert employe["actif"] is True


@pytest.mark.asyncio
async def test_creer_materiel(client: AsyncClient):
    materiel = await create_materiel(client, quantite=5)
    assert materiel["quantite"] == 5
    assert materiel["quantite_disponible"] == 5


@pytest.mark.asyncio
async def test_affecter_un_materiel(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=10)
    resp = await client.post(
        "/api/v1/affectations",
        json={
            "employe_id": employe["id"],
            "items": [
                {"equipement_id": materiel["id"], "quantite": 2, "etat_affectation": "bon"}
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["statut"] == "active"
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_affecter_plusieurs_materiels(client: AsyncClient):
    employe = await create_employe(client)
    m1 = await create_materiel(client, quantite=10)
    m2 = await create_materiel(client, quantite=10)
    resp = await client.post(
        "/api/v1/affectations",
        json={
            "employe_id": employe["id"],
            "items": [
                {"equipement_id": m1["id"], "quantite": 1, "etat_affectation": "bon"},
                {"equipement_id": m2["id"], "quantite": 1, "etat_affectation": "neuf"},
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    assert len(resp.json()["items"]) == 2


@pytest.mark.asyncio
async def test_empecher_affectation_superieure_stock(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=3)
    resp = await client.post(
        "/api/v1/affectations",
        json={
            "employe_id": employe["id"],
            "items": [{"equipement_id": materiel["id"], "quantite": 10}],
        },
    )
    assert resp.status_code == 400
    assert "disponible" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_retourner_materiel(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=10)
    resp = await client.post(
        "/api/v1/affectations",
        json={
            "employe_id": employe["id"],
            "items": [{"equipement_id": materiel["id"], "quantite": 2}],
        },
    )
    aff = resp.json()
    item_id = aff["items"][0]["id"]
    resp = await client.post(
        f"/api/v1/affectations/{aff['id']}/retour",
        json={
            "items": [
                {
                    "affectation_item_id": item_id,
                    "quantite_retournee": 2,
                    "etat_retour": "bon",
                }
            ]
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["statut"] == "retournee"


@pytest.mark.asyncio
async def test_quantites_mises_a_jour_auto(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=10)
    eid = materiel["id"]

    # Affecter 3 → dispo 7
    resp = await client.post(
        "/api/v1/affectations",
        json={"employe_id": employe["id"], "items": [{"equipement_id": eid, "quantite": 3}]},
    )
    aff_id = resp.json()["id"]
    item_id = resp.json()["items"][0]["id"]
    r = await client.get(f"/api/v1/equipements/{eid}")
    assert r.json()["quantite_disponible"] == 7

    # Retourner 1 → dispo 8
    await client.post(
        f"/api/v1/affectations/{aff_id}/retour",
        json={
            "items": [
                {"affectation_item_id": item_id, "quantite_retournee": 1, "etat_retour": "bon"}
            ]
        },
    )
    r = await client.get(f"/api/v1/equipements/{eid}")
    assert r.json()["quantite_disponible"] == 8


@pytest.mark.asyncio
async def test_empecher_affectation_en_maintenance(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=5)
    # Passer en maintenance.
    r = await client.post(
        f"/api/v1/maintenances/equipement/{materiel['id']}",
        json={"date_debut": "2026-08-22", "motif": "Test maintenance"},
    )
    assert r.status_code == 201, r.text
    # Affectation doit etre refusee.
    r = await client.post(
        "/api/v1/affectations",
        json={"employe_id": employe["id"], "items": [{"equipement_id": materiel["id"], "quantite": 1}]},
    )
    assert r.status_code == 400
    assert "maintenance" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_enregistrer_chaque_mouvement(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=10)
    await client.post(
        "/api/v1/affectations",
        json={"employe_id": employe["id"], "items": [{"equipement_id": materiel["id"], "quantite": 2}]},
    )
    r = await client.get(f"/api/v1/mouvements?equipement_id={materiel['id']}")
    assert r.status_code == 200
    assert any(m["type"] == "affectation" for m in r.json()["items"])


@pytest.mark.asyncio
async def test_historique_conserve(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=10)
    await client.post(
        "/api/v1/affectations",
        json={"employe_id": employe["id"], "items": [{"equipement_id": materiel["id"], "quantite": 1}]},
    )
    r = await client.get(f"/api/v1/mouvements?equipement_id={materiel['id']}")
    # L'ancien employe reste dans l'historique (mouvement conserve employe_id).
    assert any(m["employe_id"] == employe["id"] for m in r.json()["items"])


@pytest.mark.asyncio
async def test_permissions_employe_consulte_ses_materiels(client: AsyncClient):
    # L'employe peut consulter ses propres materiels via /employes/moi (actif requis).
    r = await client.get("/api/v1/employes/moi")
    # Superadmin n'a pas de fiche employe liee → liste vide (200, pas 403).
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_quantite_negative_interdite(client: AsyncClient):
    employe = await create_employe(client)
    materiel = await create_materiel(client, quantite=10)
    r = await client.post(
        "/api/v1/affectations",
        json={
            "employe_id": employe["id"],
            "items": [{"equipement_id": materiel["id"], "quantite": -1}],
        },
    )
    # Validation Pydantic (ge=1) → 422.
    assert r.status_code == 422
