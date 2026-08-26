# Guide du projet BeStock — Fichiers et dossiers

Document de référence décrivant **chaque dossier et chaque fichier** du projet, avec les
spécifications techniques associées.

---

## 1. Racine du projet

| Élément | Rôle |
|---------|------|
| `README.md` | Présentation générale : démarrage rapide, structure, sécurité, optimisations |
| `docker-compose.prod.yml` | Déploiement production durci : réseau interne isolé, ports liés à localhost uniquement, secrets par variables d'environnement |
| `package.json` | Raccourci racine : `npm run dev` délègue au dossier `frontend/` |
| `package-lock.json` | Verrou des dépendances du raccourci racine |
| `.gitignore` | Exclut les secrets centralisés (`env/.env`, `env/.env.production`) |
| `.git/` | Historique git (ne jamais modifier manuellement) |

### 1.1 Configuration centralisée (`env/`)

Tous les fichiers d'environnement sont regroupés dans `env/` à la racine :

| Fichier | Rôle |
|---------|------|
| `env/.env` | Configuration locale réelle — **jamais commité** (dans `.gitignore`) |
| `env/.env.example` | Modèle public des variables d'environnement (commité) |
| `env/.env.production` | Gabarit de configuration production sécurisée — **jamais commité** |

Le backend charge automatiquement `env/.env` (chemin résolu depuis `app/core/config.py`,
indépendant du répertoire courant). Surcharge possible via la variable `ENV_FILE`.

---

## 2. Backend (`backend/`) — API FastAPI + PostgreSQL

### 2.1 Fichiers racine du backend

| Fichier | Rôle |
|---------|------|
| `Dockerfile` | Image de l'API basée sur `solaris-2026-main-api:latest` (Python 3.12 + toutes les dépendances préinstallées). Copie `app/`, expose 8000, lance uvicorn |
| `docker-compose.yml` | Environnement **dev** : service `db` (postgres:16-alpine, port 5432) + service `api` (build local, port 8000). Le seed s'exécute automatiquement avant uvicorn |
| `requirements.txt` | Versions exactes des dépendances (documentatif : l'image de base les fournit déjà) |
| `.gitignore` | Exclut `.env`, caches Python… |

**Dépendances principales** : fastapi, uvicorn[standard], sqlalchemy 2 async, asyncpg,
pydantic-settings, PyJWT, bcrypt, python-dotenv, email-validator.

### 2.2 Point d'entrée

| Fichier | Rôle |
|---------|------|
| `app/main.py` | Crée l'application FastAPI : middlewares (headers sécurité → rate limiting → CORS), montage du routeur `/api/v1`, endpoint `/health` |
| `app/internal_data.py` | Script d'initialisation exécuté au démarrage du conteneur : crée les tables, applique la migration `userrole`, lance le seed |
| `app/__init__.py` | Marqueur de package Python (vide par convention) |

> Les fichiers `__init__.py` vides présents dans chaque sous-dossier sont **indispensables** :
> ils transforment les dossiers en packages Python importables.

### 2.3 `app/api/` — Couche HTTP

| Fichier | Rôle |
|---------|------|
| `router.py` | Agrège les 7 sous-routeurs et les expose sous `/api/v1` |
| `deps.py` | Dépendances FastAPI partagées : session DB (`DbSession`), extraction du JWT (`TokenDep`), utilisateur courant (`get_current_user`), contrôle d'activité (403 si inactif), contrôle de rôles (`RolesDep`), récupération IP cliente |
| `routes/auth.py` | `/auth` : register (201), login/json, refresh, logout (204), me 🔒 |
| `routes/users.py` | `/users` 🔒 superadmin : liste paginée, détail, création, modification, suppression |
| `routes/equipements.py` | `/equipements` 🔒 : CRUD complet + `/stats` (dashboard) + `/{id}/historique` |
| `routes/categories.py` | `/categories` 🔒 : liste (lecture seule) |
| `routes/statuts.py` | `/statuts` 🔒 : liste (lecture seule) |
| `routes/emplacements.py` | `/emplacements` 🔒 : liste (lecture seule) |
| `routes/historique.py` | `/historique` 🔒 : journal global paginé |

Légende : 🔒 = authentification requise.

### 2.4 `app/core/` — Configuration et cryptographie

| Fichier | Rôle |
|---------|------|
| `config.py` | Classe `Settings` (pydantic-settings) : lit `.env`. Variables : DATABASE_URL, SECRET_KEY, ALGORITHM, durées des tokens, FIRST_SUPERUSER_*, BACKEND_CORS_ORIGINS. Cache via `@lru_cache` |
| `security.py` | Primitives crypto : `hash_password` / `verify_password` (bcrypt, limite 72 octets gérée), `create_access_token` / `decode_access_token` (JWT HS256, liste blanche d'algorithmes), `generate_refresh_token` (secrets.token_urlsafe(48)), `hash_refresh_token` (SHA-256) |

### 2.5 `app/models/` — Schéma de base (SQLAlchemy)

| Fichier | Table | Points clés |
|---------|-------|-------------|
| `user.py` | `users` | Enum `UserRole` (superadmin/admin/manager), username et email uniques |
| `category.py` | `categories` | nom unique, flag `actif`, relation 1-N équipements |
| `statut.py` | `statuts` | nom unique (Fonctionnel/Défectueux/En maintenance seedés) |
| `emplacement.py` | `emplacements` | nom + batiment/etage/salle |
| `equipement.py` | `equipements` | référence unique, FK categorie/statut (non null) + emplacement (nullable), created_by/updated_by, index sur les 3 FK |
| `historique.py` | `historique` | journal d'audit : action, valeurs avant/après, IP, auteur |
| `refresh_token.py` | `refresh_tokens` | token_hash SHA-256 (jamais le token en clair) |
| `__init__.py` | — | importe tous les modèles pour `Base.metadata` |

### 2.6 `app/schemas/` — Contrats Pydantic (validation entrée/sortie)

| Fichier | Contenu |
|---------|---------|
| `user.py` | `UserCreate` (inscription, mdp ≥ 8), `UserAdminCreate` (rôle imposé), `UserRead`, `UserUpdate`, `UserList` |
| `token.py` | `LoginRequest`, `RefreshRequest`, `Token` (access + refresh + type) |
| `equipement.py` | `EquipementCreate/Update/Read/List/Stats` — longueurs alignées sur SQL (reference ≤ 50, nom ≤ 150…) |
| `category.py`, `statut.py`, `emplacement.py` | Create/Update/Read par référentiel |
| `historique.py` | `HistoriqueRead` avec `utilisateur_nom` calculé |

Toute requête invalide est rejetée en **422 avant tout accès base** (anti-injection).

### 2.7 `app/crud/` — Accès aux données

Un fichier par entité, fonctions async réutilisables :

| Fichier | Fonctions notables |
|---------|--------------------|
| `user.py` | get_by_email (email normalisé en minuscules), authenticate, list_users paginée, update (re-hash du mot de passe si fourni) |
| `equipement.py` | list filtrable par catégorie, count_total, count_by_statut, list_recent(8) |
| `refresh_token.py` | create (hache le token), get_by_token (comparaison par hash), delete/révocation |
| `historique.py` | insert journal, list_historique, list_for_equipement |
| `category.py`, `statut.py`, `emplacement.py` | CRUD standard + `get_by_nom` |

### 2.8 `app/services/` — Logique métier

| Fichier | Rôle |
|---------|------|
| `auth.py` | register (compte manager inactif), login (vérifie bcrypt + is_active), refresh avec rotation + révocation de l'ancien token, logout |
| `equipement.py` | create/update/delete : applique les règles métier puis **journalise dans historique** (auteur, avant/après, IP) |
| `user.py` | get_or_404, création admin, update (auto-protection : le dernier superadmin ne peut pas se rétrograder/supprimer), delete |

### 2.9 `app/db/` — Base de données

| Fichier | Rôle |
|---------|------|
| `base.py` | `DeclarativeBase` : classe mère de tous les modèles |
| `session.py` | Moteur async (`create_async_engine`, pool_pre_ping) + fabrique de sessions `AsyncSessionLocal` |
| `init.py` | `create_tables()` + migration idempotente du type enum `userrole` |
| `seed.py` | Seed idempotent : superadmin (depuis env), 3 catégories, 3 statuts, 2 emplacements |
| `__init__.py` | Ré-exports pratiques |

### 2.10 `app/middleware/` — Middlewares transverses

| Fichier | Rôle |
|---------|------|
| `security_headers.py` | Ajoute CSP, X-Frame-Options DENY, nosniff, Referrer-Policy, Permissions-Policy à chaque réponse |
| `rate_limit.py` | Limiteur maison pur Starlette (zéro dépendance) : fenêtre glissante en mémoire par IP — login/register 5/min, refresh/logout 10/min → 429 + Retry-After |

---

## 3. Frontend (`frontend/`) — Nuxt 4

### 3.1 Fichiers racine

| Fichier | Rôle |
|---------|------|
| `package.json` | Scripts (`dev`, `build`, `generate`, `preview`) + dépendances (nuxt, vue, pinia, axios…) |
| `nuxt.config.ts` | Modules (tailwind, fonts, icon, image, pinia), config icônes bundleées, variables publiques |
| `tsconfig.json` | Config TypeScript (le code reste majoritairement JS) |
| `.gitignore` | Exclut node_modules, .nuxt, .output, dist |
| `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `package-lock.json` | Verrous de dépendances (npm ET pnpm) |

### 3.2 `frontend/app/` — Cœur applicatif

| Fichier | Rôle |
|---------|------|
| `app.vue` | Composant racine (montre `<NuxtLayout><NuxtPage/>)` |

### 3.3 `app/pages/` — Vues (routage par fichiers)

| Fichier | Route | Rôle |
|---------|-------|------|
| `index.vue` | `/` | Landing page publique |
| `connexion.vue` | `/connexion` | Formulaire de connexion |
| `inscription.vue` | `/inscription` | Création de compte |
| `dashboard.vue` | `/dashboard` 🔒 | **Centre de contrôle SaaS** : QuickActions + 4 stats principales + indicateurs compacts + StockOverview (6 segments) + AlertsPanel + Affectations récentes + ActivityFeed (6 derniers historiques) + MaterialTable (8 récents) — branché sur `GET /equipements/stats` + `GET /historique` |
| `materiel/nouveau.vue` | `/materiel/nouveau` 🔒 | Formulaire de création d'équipement |
| `materiel/[categoryId]/[id].vue` | dynamique 🔒 | Vue imbriquée catégorie → équipement |
| `equipements/[id].vue` | `/equipements/:id` 🔒 | Fiche détaillée + historique de l'équipement |
| `categories/index.vue` | `/categories` 🔒 | Liste des catégories (avec icônes) |
| `categories/[id].vue` | `/categories/:id` 🔒 | Équipements filtrés par catégorie |
| `employes/index.vue` | `/employes` 🔒 | Liste, création et détail employés |
| `affectations/index.vue` | `/affectations` 🔒 | Liste des affectations, création multi-matériels |
| `maintenance.vue` | `/maintenance` 🔒 | Suivi maintenances + clôtures |
| `historique.vue` | `/historique` 🔒 | Journal global (qui, quoi, avant/après, quand) |
| `users/index.vue` | `/users` 🔒 superadmin | Gestion des comptes (activer, rôles, supprimer) |
| `compte.vue` | `/compte` 🔒 | Profil personnel |

### 3.4 `app/stores/` — État global Pinia

| Store | Rôle |
|-------|------|
| `auth.js` | Session : tokens (localStorage `bestock_token`/`bestock_refresh`/`bestock_user`), user courant, `hydrate()` |
| `categories.js` | Référentiels `categories/statuts/emplacements` + `_loaded`, `pickIcon()`, `fieldsFor(categoryId)` |
| `equipements.js` | Catalogue (`/equipements`) + `stats` (`/equipements/stats` : total, disponibles, affectes, maintenance, endommages, perdus, hors_service, affectations_actives, retours_total, affectations_recentes, recent) + getters `totalStock`, `maintenanceCount`, `recentMaterials`; invalidation `_loadedStats` après CUD |
| `affectations.js` | Affectations (`/affectations`, `/affectations/{id}/retour`) + `total` |
| `maintenances.js` | Maintenances (`/maintenances`, `demarrer`, `cloturer`) |
| `employes.js` | Employés (`/employes`) + `fetchMesMateriels()` |
| `historique.js` | Journal global + par équipement (`/historique`, `/equipements/{id}/historique`) |
| `users.js` | CRUD comptes (superadmin) |

Pattern commun : `fetch(force=false)` ne rappelle l'API que si nécessaire.

### 3.5 `app/utils/`, `app/composables/`, `app/plugins/`, `app/middleware/`

| Fichier | Rôle |
|---------|------|
| `utils/api.js` | Client axios centralisé : base URL configurable (`NUXT_PUBLIC_API_BASE`), injection du Bearer token, **intercepteur 401** → refresh silencieux (anti-course avec `refreshPromise`) puis rejeu de la requête ; échec → purge localStorage + redirection `/connexion` |
| `utils/errors.js` | Normalisation des messages d'erreur API pour affichage |
| `utils/permissions.js` | Miroir frontend de la matrice RBAC (`ROLE_PERMISSIONS`, `roleHas()`) |
| `composables/useRole.js` | `useRole()` : `role`, `isEmploye/isManager/isAdmin/canWrite`, `can(permission)` — pilote sidebar dynamique et masquage des actions |
| `composables/useToast.js` | Notifications toast (succès/erreur) |
| `composables/useConfirm.js` | Dialogues de confirmation (suppressions) |
| `plugins/auth.client.js` | Au boot client : restaure la session depuis localStorage |
| `middleware/auth.global.js` | Garde globale : routes protégées sans session → `/connexion` |

### 3.6 `app/components/` — Composants réutilisables

| Dossier/Fichier | Rôle |
|-----------------|------|
| `dashboard/DashboardStatCard.vue` | Card stat principale SaaS (chiffre 28px, icône colorée `variant` default/success/info/warning/danger, lien `Voir`) |
| `dashboard/QuickActions.vue` | 4 actions rapides → routes réelles (`/materiel/nouveau`, `/affectations/nouvelle`, `/employes`, `/affectations`) |
| `dashboard/StockOverview.vue` | Répartition stock 6 segments sans librairie (barres + pile, couleurs Disponible `#10b981` etc.) |
| `dashboard/AlertsPanel.vue` | Attention requise : maintenance/endommagés/perdus/hors service avec `Voir →` + empty `Aucune alerte` |
| `dashboard/ActivityFeed.vue` | 6 dernières activités (`historique` + nom équipement via `equipements` store), skeletons + empty |
| `dashboard/MaterialTable.vue` | Tableau 8 matériels récents, `statusMeta()` mappe `statut.nom` → couleur/dot, empty CTA |
| `dashboard/SummaryCard.vue` | Card legacy (conservée pour compatibilité, non utilisée sur le nouveau dashboard) |
| `landingpage/hero.vue`, `Fonctionnalites.vue`, `objectifs.vue`, `dev.vue` | Sections de la landing |
| `landingpage/Navabar.vue`, `connexion.vue`, `Inscription.vue` | Navigation publique + formulaires embarqués |
| `ui/Card.vue`, `Input.vue`, `Select.vue`, `Textarea.vue` | Champs de formulaire stylés |
| `ui/ConfirmDialog.vue`, `Toast.vue` | Feedback utilisateur |

### 3.7 Autres dossiers frontend

| Dossier | Rôle |
|---------|------|
| `layouts/default.vue` | Coquille publique |
| `layouts/dashboard.vue` | Coquille SaaS : sidebar `w-[264px]` bg `#0f2a4a` (Principal/Administration + CTA + bloc utilisateur) + header sticky `h-[64px]` `bg-white/80 backdrop-blur` (breadcrumbs, recherche `→ /categories?q=`, notifications dot, profil `rounded-full`) + `initials`/`hasAlerts` computeds |
| `images/` | Photos de l'équipe (larick.jpg, naim.jpg, odilon.jpg) affichées sur la landing |
| `public/` | favicon.ico, robots.txt servis tels quels |

---

## 4. Documentation (`docs/`)

| Fichier | Contenu |
|---------|---------|
| `README.md` | Sommaire de la documentation |
| `01-presentation.md` … `07-frontend.md` | Les 7 chapitres thématiques |
| `Documentation_Bestock.pdf` | Version PDF consolidée (25 pages) |
| `guide-fichiers.md` | Le présent document |
| `Guide_Fichiers_BeStock.pdf` | Version PDF du présent document |

---

## 5. Dossiers générés (à ne pas versionner)

Créés automatiquement par les outils — supprimables sans risque :

| Dossier | Généré par | Régénérable via |
|---------|-----------|-----------------|
| `frontend/node_modules/` | npm/pnpm install | `npm install` |
| `frontend/.nuxt/` | dev server Nuxt | `npm run dev` |
| `frontend/.output/`, `dist/` | build Nuxt/Nitro | `npm run build` |
| `backend/**/__pycache__/` | interpréteur Python | automatique à l'exécution |

---

## 6. Spécifications techniques

### Ports et services

| Service | Port | Notes |
|---------|------|-------|
| Frontend Nuxt | 3000 | dev server |
| API FastAPI | 8000 | publié sur 127.0.0.1 en prod (reverse proxy requis) |
| PostgreSQL | 5432 | conteneur `bestock_db`, volume `postgres_data` |

### Flux d'authentification

```
login → {access_token (30 min), refresh_token (7 j)}
     → access stocké côté client, envoyé en Bearer
401  → POST /auth/refresh (rotation, ancien révoqué)
     → rejeu automatique de la requête initiale
logout → révocation du refresh token
```

### Conventions de code

| Sujet | Convention |
|-------|------------|
| Backend | Python typé (PEP 604 `int \| None`), docstrings FR courtes, async partout |
| Frontend | JavaScript (pas de TS imposé), Composition API Vue 3 |
| Commits nomenclature tables | pluriel anglais simple : `users`, `equipements`, `historique` |
| Validation | systématiquement dans `schemas/`, jamais dans les routes |

### Cycle de vie d'un équipement (traçabilité)

```
POST   /equipements      → historique(action=creation)
PUT    /equipements/{id} → historique(action=modification, avant/après)
DELETE /equipements/{id} → historique(action=suppression)
```
Chaque entrée enregistre : auteur (`utilisateur_id`), horodatage, adresse IP.
