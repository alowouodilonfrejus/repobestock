# BeStock

Plateforme de gestion de stocks et d'inventaire : frontend **Nuxt 4 / Vue 3** + backend **FastAPI / SQLAlchemy 2 async / PostgreSQL 16**.

## Architecture

```
┌─────────────────────┐   HTTP / JWT   ┌──────────────────┐   SQL   ┌──────────────┐
│  Frontend (Nuxt 4)  │ ─────────────► │ Backend FastAPI  │ ──────► │ PostgreSQL 16 │
│  Vue 3 / Pinia      │ :3000         │ SQLAlchemy 2 async│         │              │
└─────────────────────┘               └──────────────────┘         └──────────────┘
      frontend/                                backend/                  backend/docker
```

## Structure du projet

```
bestock-main/
├── frontend/                   # Frontend Nuxt 4
│   ├── app/                    # Source de l'application
│   │   ├── components/         # landingpage/, dashboard/, ui/
│   │   ├── layouts/            # default, dashboard (sidebar)
│   │   ├── middleware/         # auth.global.js (routes protégées)
│   │   ├── pages/              # index, connexion, inscription, dashboard,
│   │   │                       #   categories/, materiel/, equipements/, historique, compte
│   │   ├── plugins/            # auth.client.js (hydratation du store)
│   │   ├── stores/             # Pinia : auth, categories, equipements, historique, users
│   │   └── utils/api.js        # client axios → http://localhost:8000/api/v1
│   ├── public/                 # fichiers statiques
│   ├── nuxt.config.ts
│   └── package.json
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/         # auth, categories, statuts, emplacements,
│   │   │   │                   #   equipements, historique, users
│   │   │   ├── deps.py         # dépendances (session DB, user courant, rôles)
│   │   │   └── router.py       # agrégation des routes
│   │   ├── core/               # config (pydantic-settings), security (JWT/bcrypt)
│   │   ├── crud/               # accès base par entité
│   │   ├── db/                 # session async (asyncpg), init, migrations, seed
│   │   ├── models/             # User, Category, Statut, Emplacement, Equipement, Historique
│   │   ├── schemas/            # schémas Pydantic
│   │   └── services/           # logique métier (auth, user, equipement)
│   ├── Dockerfile
│   ├── docker-compose.yml      # db (postgres:16) + api (fastapi)
│   └── requirements.txt
├── docs/                       # documentation Word + diagrammes UML
│   └── uml/                    # Diagrammes UML (classes, use case, séquence)
└── README.md
```

## Prérequis

- Docker + Docker Compose
- Node.js ≥ 20 (npm / pnpm)
- Python ≥ 3.11 (seulement pour un dev backend hors Docker)

## Démarrage rapide

### 1. Backend (API + base de données)

```bash
cd backend
docker compose up -d --build
```

- **API** : http://localhost:8000 — docs Swagger : http://localhost:8000/api/v1/openapi.json
- **PostgreSQL** : localhost:5432 (bestock_db / postgres / postgres)

Le conteneur `api` exécute automatiquement le seed (création des tables + données initiales).

**Compte super admin par défaut**

| Email | Mot de passe |
|---|---|
| `admin@bestock.dev` | `admin1234` |

Configurable via variables d'environnement (voir `backend/.env.example`) :
`FIRST_SUPERUSER_EMAIL`, `FIRST_SUPERUSER_PASSWORD`, `DATABASE_URL`, `SECRET_KEY`.

### 2. Frontend

```bash
# depuis la racine du projet (package.json racine qui délègue à frontend/)
npm run dev

# ou directement dans le dossier frontend
cd frontend
npm run dev
```

Frontend sur **http://localhost:3000** — le client API pointe vers `http://localhost:8000/api/v1` (configuré dans `frontend/app/utils/api.js`).

## Architecture du code (layers)

Le backend suit une architecture en couches, chaque couche a une responsabilité unique :

```
routes/  (HTTP : validation des entrées, réponses)
   ↓
services/  (logique métier : règles, garde-fous, journalisation)
   ↓
crud/  (accès aux données : requêtes SQLAlchemy)
   ↓
models/  (schéma de la base de données)
```

Le frontend suit le même principe avec des stores Pinia ciblés :

```
pages/  (vue, navigation)
   ↓
stores/  (état global + actions API : auth, categories, equipements, historique, users)
   ↓
utils/api.js  (client axios + gestion des tokens / refresh)
```

### Icônes SVG

Le projet utilise de vraies icônes SVG via le module **@nuxt/icon** (collections **heroicons** et **mdi** installées localement dans `frontend/node_modules/@iconify-json/`). Les icônes sont bundleées dans le build (aucun appel réseau au runtime) :

- Composant global : `<Icon name="heroicons:home" class="h-5 w-5" />`
- Configuré dans `frontend/nuxt.config.ts` : `icon.serverBundle.collections` (rendu SSR) + `icon.clientBundle.scan` (les icônes utilisées sont détectées automatiquement et embarquées dans le bundle client — aucun appel réseau en dev comme en prod)
- Les catégories utilisent des icônes dynamiques via le store `app/stores/categories.js` (`pickIcon` retourne un nom d'icône heroicons selon la catégorie)

## Historique des actions

Chaque action (création, modification, suppression) est journalisée dans la table `historique` avec :

- l'équipement concerné
- **le nom de l'utilisateur** (`utilisateur_nom` : `username` ou email, joint via la relation `utilisateur` sur le modèle `Historique`)
- les valeurs avant / après (`ancienne_valeur`, `nouvelle_valeur`)
- la date et l'adresse IP

L'API renvoie le champ `utilisateur_nom` dans `GET /api/v1/historique` et `GET /api/v1/equipements/{id}/historique` (affiché sur `frontend/app/pages/historique.vue` et `equipements/[id].vue`).

## Validation des entrées (API)

Les schémas Pydantic (`backend/app/schemas/`) valident les entrées avant tout accès base de données :

- **Mot de passe** : minimum **8 caractères** (`Field(min_length=8)`)
- **Champs texte** : longueur maximale alignée sur les colonnes SQL (ex. `reference` ≤ 50, `nom` ≤ 150, `marque`/`modele` ≤ 100, `numero_serie` ≤ 150) — un dépassement renvoie un **422** clair plutôt qu'une erreur 500 de la base
- Rôles : enum (`manager` / `admin` / `superadmin`) — toute autre valeur → 422

## Optimisations (charges réseau réduites)

- **Endpoint `GET /api/v1/equipements/stats`** : le dashboard et la page historique utilisent ce nouvel endpoint léger (3 requêtes SQL : total, maintenance, 8 récents) au lieu de télécharger le catalogue complet.
- **Cache Pinia côté client** : les stores `categories`, `equipements` et `historique` gardent leurs données en mémoire (`_loaded`) et ne refont un appel API que si nécessaire (`force=true` pour un refresh manuel). Les référentiels (catégories/statuts/emplacements) ne sont chargés qu'une seule fois par session.
- **Invalidation automatique** : après une création/modification/suppression, le cache du dashboard est marqué obsolète pour se recharger au prochain affichage.
- **Pagination** : les endpoints de liste supportent `skip`/`limit` (défaut 100, max 500 pour les équipements ; 200 pour l'historique).