# 5. Modèles de données

## Vue d'ensemble

Base **PostgreSQL 16**, accès via **SQLAlchemy 2 async** (driver `asyncpg`).

```
users ──┐
        ├──< equipements >──┬── categories
        │        │          ├── statuts
        │        └──────────┴── emplacements
        ├──< historique >───┴── equipements
        └──< refresh_tokens
```

## Tables

### `users`

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto-increment |
| username | VARCHAR(50) | unique, non null |
| email | VARCHAR(100) | unique, non null |
| hashed_password | VARCHAR(255) | non null (bcrypt) |
| is_active | BOOLEAN | défaut `true` |
| role | ENUM `userrole` | `superadmin` / `admin` / `manager`, défaut `manager` |
| created_at / updated_at | TIMESTAMPTZ | auto |

> Un compte issu de l'inscription publique (`POST /employes/inscription`) naît avec
> `role=employe` et
> `is_active=false` : il ne peut pas se connecter tant que le super admin l'active.

### `categories`

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK |
| nom | VARCHAR(100) | unique, non null |
| description | TEXT | nullable |
| actif | BOOLEAN | défaut `true` |

Relation 1-N vers `equipements`.

### `statuts`

Même structure que `categories` (nom en VARCHAR(50)). Valeurs seedées :
**Fonctionnel**, **Défectueux**, **En maintenance**.

### `emplacements`

| Colonne | Type |
|---------|------|
| id | INTEGER PK |
| nom | VARCHAR(100), non null |
| batiment | VARCHAR(100) |
| etage | VARCHAR(50) |
| salle | VARCHAR(100) |
| description | TEXT |
| actif | BOOLEAN |

Permet une localisation fine : *Entrepôt / Bâtiment B / Étage 2 / Salle 204*.

### `equipements` (table centrale)

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK |
| reference | VARCHAR(50) | **unique**, non null |
| nom | VARCHAR(150) | non null |
| description | TEXT | nullable |
| marque / modele | VARCHAR(100) | nullable |
| numero_serie | VARCHAR(150) | **unique**, nullable |
| date_acquisition | DATE | nullable |
| categorie_id | FK → categories.id | **non null**, indexé |
| statut_id | FK → statuts.id | **non null**, indexé |
| emplacement_id | FK → emplacements.id | nullable, indexé |
| created_by / updated_by | FK → users.id | nullable (traçabilité) |
| created_at / updated_at | TIMESTAMPTZ | auto |

Relations ORM résolues dans les réponses API : `categorie`, `statut`, `emplacement`.

### `historique` (journal d'audit)

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | PK |
| utilisateur_id | FK → users.id | auteur de l'action (nullable) |
| equipement_id | FK → equipements.id | équipement concerné (nullable) |
| action | VARCHAR(50) | ex. `creation`, `modification`, `suppression` |
| ancienne_valeur | TEXT | JSON des valeurs avant modification |
| nouvelle_valeur | TEXT | JSON des valeurs après |
| date_action | TIMESTAMPTZ | horodatage |
| adresse_ip | VARCHAR(50) | IP cliente |

La colonne calculée `utilisateur_nom` est renvoyée par l'API (jointure sur `users`,
affiche `username` sinon email).

### `refresh_tokens`

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | PK |
| user_id | FK → users.id | propriétaire |
| token_hash | CHAR(64) | SHA-256 du token — **jamais le token en clair** |
| expire le champ d'expiration | TIMESTAMPTZ | contrôle à chaque usage |

Un refresh token n'est vérifiable que par hachage comparé : une fuite de la base
ne permet pas de reconstruire les tokens.

## Migrations

Le schéma est créé et mis à jour au démarrage du conteneur par `app/db/init.py`
(création des tables + migrations légères idempotentes, ex. renommage du type
enum `userrole`). Pas d'outil Alembic : les évolutions sont gérées par ce script.

## Seed (`app/db/seed.py`)

Idempotent, exécuté à chaque démarrage :

1. Super admin depuis `FIRST_SUPERUSER_*` (ignoré si l'email existe déjà)
2. Catégories : Informatique, Immobilier, Nettoyage
3. Statuts : Fonctionnel, Défectueux, En maintenance
4. Emplacements : Entrepôt, Bureau
