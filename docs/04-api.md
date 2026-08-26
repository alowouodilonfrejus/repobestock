# 4. API REST

## Généralités

- **Base URL** : `http://localhost:8000/api/v1`
- **Format** : JSON partout (sauf `DELETE` qui renvoie `204 No Content`)
- **Authentification** : header `Authorization: Bearer <access_token>`
- **Docs interactive** : http://localhost:8000/docs

### Codes de retour standards

| Code | Signification |
|------|---------------|
| 200 / 201 / 204 | Succès |
| 401 | Token absent, invalide ou expiré |
| 403 | Compte inactif, ou rôle insuffisant |
| 404 | Ressource introuvable |
| 422 | Payload invalide (validation Pydantic) — détail dans `detail` |
| 429 | Trop de requêtes (rate limiting) |

---

## Authentification — `/auth`

> ℹ️ L'ancien endpoint `/auth/register` a été **supprimé** : l'inscription publique
passe exclusivement par `POST /employes/inscription` (voir section Employés), qui crée
le compte inactif **et** la fiche collaborateur liée en une transaction.

### `POST /auth/login/json` → 200
```json
{ "email": "admin@bestock.dev", "password": "••••" }
```
```json
{
  "access_token": "eyJ...",
  "refresh_token": "chaîne-opaque-64-caractères",
  "token_type": "bearer"
}
```
> Rate limité à **5 req/min/IP**.

### `POST /auth/refresh` → 200
Échange un refresh token valide contre un nouveau couple (rotation) :
```json
{ "refresh_token": "..." }
```
→ même format que login. L'ancien refresh token est révoqué.

### `POST /auth/logout` → 204
Révoque le refresh token fourni.

### `GET /auth/me` → 200 🔒
Profil de l'utilisateur connecté (`UserRead`).

---

## Utilisateurs — `/users` 🔒 RBAC

Permissions (matrice centralisée : `app/core/permissions.py` — `ADMIN` n'a plus `users:*`) :

| Méthode | Route | Permission | Rôles |
|---------|-------|-----------|-------|
| GET | `/users?skip=0&limit=50` | `users:read` | **superadmin seul** |
| GET | `/users/{id}` | `users:read` | **superadmin seul** |
| POST | `/users` | `RolesDep(SUPERADMIN)` | superadmin seul |
| PUT | `/users/{id}` | `users:validate` | **superadmin seul** |
| POST | `/users/{id}/valider` | `users:validate` | **superadmin seul** — active un compte en attente (+ rôle final) |
| POST | `/users/{id}/rejeter` | `users:validate` | **superadmin seul** — supprime compte en attente + fiche liée |
| DELETE | `/users/{id}` | `RolesDep(SUPERADMIN)` | superadmin seul |

Règles serveur appliquées dans tous les cas :
- un utilisateur ne peut attribuer que des rôles **strictement inférieurs** au sien
  (sauf superadmin) ;
- interdiction de désactiver/dégrader le **dernier superadmin actif** ;
- le superadmin est exempté des blocages d'auto-modification.

`UserRead` :
```json
{
  "id": 1, "email": "admin@bestock.dev", "username": "superadmin",
  "role": "superadmin", "is_active": true,
  "created_at": "2026-08-21T10:00:00Z", "updated_at": "..."
}
```

---

## Collaborateurs — `/employes` 🔒 RBAC

| Méthode | Route | Permission | Description |
|---------|-------|-----------|-------------|
| POST | `/employes/inscription` | **public** | Inscription : compte inactif + fiche liée (matricule auto `EMP-XXX` si absent) → 201 |
| GET | `/employes?actif=` | `employes:read` | Liste (manager+) |
| GET | `/employes/{id}` | `employes:read` | Fiche détaillée |
| GET | `/employes/moi` 🔒 | connecté | Matériels actuellement attribués au compte |
| POST | `/employes` | `employes:write` | Création simple |
| POST | `/employes/avec-compte` | `employes:write` | Création + compte actif immédiat (rôle plafonné au niveau du créateur) |
| PUT | `/employes/{id}` | `employes:write` | Modification (matricule unique contrôlé) |

## Affectations — `/affectations` 🔒 RBAC

| Méthode | Route | Permission | Rôles | Description |
|---------|-------|-----------|-------|-------------|
| GET | `/affectations` · `/affectations/{id}` | `affectations:read` | superadmin, admin | Liste / détail |
| GET | `/affectations/moi` | `ActiveUser` | tous connectés | Mes affectations |
| POST | `/affectations` | `affectations:write` | **superadmin, admin** | **REST CRUD** création multi-matériels, transaction unique |
| POST | `/affectations/{id}/retour` | `affectations:write` | **superadmin, admin** | **REST CRUD** retour partiel/total |

## Maintenances — `/maintenances` 🔒 RBAC

| Méthode | Route | Permission | Rôles | Description |
|---------|-------|-----------|-------|-------------|
| GET | `/maintenances` | `maintenances:read` | superadmin, admin | Liste globale |
| GET | `/maintenances/moi` | `ActiveUser` | tous connectés | Incidents de mes matériels |
| POST | `/maintenances/equipement/{id}` | `maintenances:write` | **superadmin, admin** | **REST CRUD** déclarer en maintenance (non affectable) |
| POST | `/maintenances/{id}/cloture` | `maintenances:write` | **superadmin, admin** | **REST CRUD** clôture + coût |

## Référentiels — lecture seule 🔒

| Méthode | Route | Retour |
|---------|-------|--------|
| GET | `/categories` | `[{id, nom, description, actif}]` |
| GET | `/statuts` | `[{id, nom, description, actif}]` |
| GET | `/emplacements` | `[{id, nom, batiment, etage, salle, description, actif}]` |

Accessibles à tout utilisateur authentifié et actif.

---

## Équipements — `/equipements` 🔒

### `GET /equipements` → 200
Paramètres : `skip` (défaut 0), `limit` (1–500, défaut 100), `categorie_id` (filtre optionnel).
```json
{ "items": [EquipementRead], "total": 42, "limit": 100, "skip": 0 }
```

### `GET /equipements/stats` → 200
Endpoint léger pour le dashboard :
```json
{
  "total": 42,
  "maintenance": 3,
  "recent": [ /* 8 derniers équipements */ ]
}
```
> Paramètre optionnel `maintenance_statut_id` pour compter un autre statut.

### `POST /equipements` → 201
```json
{
  "reference": "EQ-2026-001",
  "nom": "Serveur Dell R740",
  "description": "texte libre",
  "marque": "Dell", "modele": "R740",
  "numero_serie": "SN-ABC123",
  "date_acquisition": "2026-01-15",
  "categorie_id": 1,
  "statut_id": 1,
  "emplacement_id": 2
}
```
Champs requis : `reference` (unique), `nom`, `categorie_id`, `statut_id`.
→ Journalise une entrée `historique` (action création).

### Autres

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/equipements/{id}` | Détail (avec catégorie/statut/emplacement résolus) |
| GET | `/equipements/{id}/historique` | Historique complet de l'équipement |
| PUT | `/equipements/{id}` | Modification partielle → journalisée (avant/après) |
| DELETE | `/equipements/{id}` | Suppression → journalisée |

---

## Historique — `/historique` 🔒

### `GET /historique?skip=0&limit=200` → 200
Journal global (limite max 1000). Entrée type :

```json
{
  "id": 12,
  "utilisateur_nom": "superadmin",
  "equipement_id": 5,
  "action": "modification",
  "ancienne_valeur": "{\"statut\": \"Fonctionnel\"}",
  "nouvelle_valeur": "{\"statut\": \"En maintenance\"}",
  "date_action": "2026-08-21T14:32:00Z",
  "adresse_ip": "172.21.0.1"
}
```

---

## Santé

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/health` (hors `/api/v1`) | `{ "status": "ok" }` — pour supervision |
