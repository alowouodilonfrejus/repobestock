# 2. Architecture

## Vue d'ensemble

```
┌─────────────────────┐   HTTP / JWT   ┌──────────────────┐   SQL async   ┌──────────────┐
│  Frontend (Nuxt 4)  │ ─────────────► │ Backend FastAPI  │ ────────────► │ PostgreSQL 16│
│  Vue 3 / Pinia      │   axios        │ SQLAlchemy async │   asyncpg     │              │
└─────────────────────┘                └──────────────────┘               └──────────────┘
      :3000                                 :8000                         :5432
```

- **Communication frontend ↔ backend** : REST + JSON, tokens Bearer (access) et refresh token
- **Backend ↔ base** : driver `asyncpg`, sessions SQLAlchemy asynchrones
- **Conteneurs** : `bestock_db` (postgres:16-alpine), `bestock_api` (FastAPI + uvicorn)

## Architecture en couches (backend)

Le backend suit une séparation stricte des responsabilités — chaque couche ne connaît
que celle immédiatement en dessous :

```
api/routes/       HTTP : validation des entrées, codes de réponse, dépendances
    ↓
services/         logique métier : règles, garde-fous, journalisation historique
    ↓
crud/             accès aux données : requêtes SQLAlchemy réutilisables
    ↓
models/           schéma de la base (tables SQLAlchemy)
```

### Responsabilités par dossier

| Dossier | Rôle | Exemple |
|---------|------|---------|
| `app/api/routes/` | Endpoints REST, typage Pydantic | `equipements.py` expose GET/POST/PUT/DELETE |
| `app/api/deps.py` | Dépendances FastAPI : session DB, utilisateur courant, role guards | `PermDep("stock:write")` |
| `app/core/permissions.py` | Matrice RBAC centralisée (rôle → permissions). Source de vérité unique côté API | `role_has(role, "affectations:write")` |
| `app/services/` | Règles métier + journalisation | `create_equipement()` écrit aussi dans `historique` |
| `app/crud/` | Requêtes DB génériques | `list_equipements(db, skip, limit)` |
| `app/models/` | Tables SQLAlchemy | `User`, `Equipement`, `Historique`… |
| `app/schemas/` | Contrats d'entrée/sortie Pydantic | `EquipementCreate`, `UserRead` |
| `app/core/config.py` | Configuration via variables d'environnement (pydantic-settings) | `SECRET_KEY`, `DATABASE_URL` |
| `app/core/security.py` | Primitives crypto : bcrypt, JWT, refresh tokens | `hash_password()`, `decode_access_token()` |
| `app/db/` | Session async, création des tables, migrations légères, seed | `seed.py` |
| `app/middleware/` | Middlewares transverses | rate limiting, headers de sécurité |

## Architecture frontend

```
pages/            vues et navigation (file-based routing Nuxt)
    ↓
stores/           état global Pinia + actions API (auth, categories, equipements, affectations, historiques…)
    ↓
utils/api.js      client axios unique : base URL, injection du token, refresh auto
```

- `middleware/auth.global.js` : garde globale — redirige vers `/connexion` si non authentifié
- `plugins/auth.client.js` : hydrate le store auth depuis le stockage local au démarrage
- `layouts/dashboard.vue` : coquille SaaS — sidebar groupée (Principal/Administration) + CTA `+ Ajouter un matériel`, header sticky avec recherche globale, notifications et profil
- `components/dashboard/` : briques réutilisables du centre de contrôle — `DashboardStatCard`, `QuickActions`, `StockOverview`, `AlertsPanel`, `ActivityFeed`, `MaterialTable` (tous branchés sur `equipements.stats` et `historique` sans données fictives)

## Cycle d'une requête authentifiée

1. Le client envoie `Authorization: Bearer <access_token>`
2. `deps.get_current_user` décode le JWT (`core/security.decode_access_token`)
3. L'utilisateur est chargé depuis la base ; s'il est inactif → **403**
4. Le garde de permission (`require_permission` → `PermDep(...)`, basé sur la matrice RBAC) peut renvoyer **403**
5. La couche service exécute la logique métier et journalise dans `historique`
6. La réponse est sérialisée via les schémas Pydantic (jamais d'objet ORM brut)

## Arborescence complète

Voir [README principal](../README.md#structure-du-projet).
