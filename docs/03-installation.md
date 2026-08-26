# 3. Installation

## Prérequis

| Outil | Version | Usage |
|-------|---------|-------|
| Docker + Docker Compose | récent | backend + base de données |
| Node.js | ≥ 20 (npm ou pnpm) | frontend |
| Python | ≥ 3.12 | uniquement pour du dev backend hors Docker |

## 1. Développement — backend (API + PostgreSQL)

```bash
cd backend
docker compose --env-file ../env/.env up -d --build
```

Au démarrage, le conteneur exécute automatiquement :

1. `python -m app.internal_data` — création des tables + seed
2. `uvicorn app.main:app --host 0.0.0.0 --port 8000`

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Docs Swagger | http://localhost:8000/docs |
| Healthcheck | http://localhost:8000/health → `{"status": "ok"}` |

### Données initiales (seed)

- **Super admin** : créé depuis les variables `FIRST_SUPERUSER_EMAIL` / `FIRST_SUPERUSER_PASSWORD`
- **Catégories** : Informatique, Immobilier, Nettoyage
- **Statuts** : Fonctionnel, Défectueux, En maintenance
- **Emplacements** : Entrepôt, Bureau

Le seed est idempotent : il ne recrée rien si les données existent déjà.

### Variables d'environnement

Copier le modèle puis adapter :

```bash
cp env/.env.example env/.env
```

| Variable | Défaut | Description |
|----------|--------|-------------|
| `POSTGRES_USER` | `postgres` | Utilisateur PostgreSQL (compose dev + prod) |
| `POSTGRES_PASSWORD` | — | Mot de passe PostgreSQL (**obligatoire**, le compose refuse de démarrer sans) |
| `POSTGRES_DB` | `bestock_db` | Nom de la base |
| `DATABASE_URL` | `postgresql+asyncpg://…@localhost:5432/bestock_db` | Connexion DB (`db` au lieu de `localhost` sous Docker) |
| `SECRET_KEY` | ⚠️ valeur d'exemple | Clé de signature JWT — **obligatoire en prod**, générer via `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ALGORITHM` | `HS256` | Algorithme JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Durée de vie access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Durée de vie refresh token |
| `FIRST_SUPERUSER_EMAIL` | `admin@bestock.dev` | Email du compte initial |
| `FIRST_SUPERUSER_PASSWORD` | — | Mot de passe initial (**fort obligatoire**) |
| `FIRST_SUPERUSER_USERNAME` | `superadmin` | Nom d'utilisateur initial |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000", "http://localhost:8080"]` | Liste blanche CORS |

> ⚠️ **Jamais de mot de passe par défaut dans le code.** Le fichier `.env` est ignoré par git.

## 2. Développement — frontend

```bash
cd frontend        # ou npm run dev depuis la racine
npm install        # première fois seulement
npm run dev
```

Frontend sur **http://localhost:3000** — le client axios cible `http://localhost:8000/api/v1`
(configurable dans `frontend/app/utils/api.js`).

## 3. Production

```bash
cp env/.env.production env/.env
# ÉDITER env/.env :
#   - mots de passe forts (DB + super admin)
#   - SECRET_KEY fraîche
#   - domaines réels dans BACKEND_CORS_ORIGINS

docker compose -f docker-compose.prod.yml --env-file env/.env up -d --build
```

Durcissements appliqués par `docker-compose.prod.yml` :

- Ports publiés sur `127.0.0.1` uniquement (reverse proxy Nginx/Traefik requis devant)
- Réseau Docker `internal` : la base n'est pas exposée publiquement
- Aucun secret en dur dans le compose — tout vient des variables d'environnement
- Uvicorn avec plusieurs workers

## Commandes utiles

```bash
# Logs de l'API
docker logs -f bestock_api

# Redémarrer proprement toute la stack
docker compose restart

# Réinitialiser complètement la base (⚠️ destructif)
docker compose --env-file ../env/.env down -v && docker compose --env-file ../env/.env up -d --build

# Shell SQL dans la base
docker exec -it bestock_db psql -U postgres -d bestock_db
```

## Résolution des problèmes

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| Port 8000 déjà utilisé | ancienne instance / autre service | `docker compose down` puis relancer |
| `address already in use` au build | conteneur orphelin | `docker compose up -d --build --force-recreate` |
| Login impossible après changement `.env` | super admin déjà seedé | modifier le mot de passe en base ou `down -v` pour re-seeder |
| 401 systématiques | `SECRET_KEY` changée → tokens invalides | se reconnecter (les anciens JWT sont rejetés) |
