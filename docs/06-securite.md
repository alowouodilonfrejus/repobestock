# 6. Sécurité

## Authentification

### Mots de passe
- Hachage **bcrypt** avec sel aléatoire (`bcrypt.hashpw` + `gensalt`)
- Vérification en temps constant via `bcrypt.checkpw`
- Limite bcrypt de 72 octets gérée explicitement (troncature contrôlée)
- Minimum **8 caractères** imposé par les schémas Pydantic

### JWT (access token)
| Propriété | Valeur |
|-----------|--------|
| Algorithme | HS256 (clé `SECRET_KEY`) |
| Durée de vie | 30 min (`ACCESS_TOKEN_EXPIRE_MINUTES`) |
| Claims | `sub` (user id), `iat`, `exp`, `type=access` |

Protections testées :
- ✅ signature falsifiée rejetée (401)
- ✅ attaque `alg:none` bloquée (liste blanche d'algorithmes dans `jwt.decode`)
- ✅ token expiré rejeté

### Refresh tokens (rotation)
- Génération cryptographique : `secrets.token_urlsafe(48)` (~64 caractères)
- Stockés **hachés SHA-256** — la base ne contient jamais le token en clair
- **Rotation à chaque usage** : `/auth/refresh` révoque l'ancien token et en émet un nouveau
- Révocation explicite via `/auth/logout`
- Durée : 7 jours

## Autorisations (RBAC)

Hiérarchie des rôles (matrice `app/core/permissions.py`) :

```
superadmin ( * )  →  tout + users:* (seul à créer/valider/supprimer des comptes)
    admin          →  CRUD stock/affectations/maintenances/employes, lecture historique — sans users:*
     manager       →  lecture seule (dashboard, referentiels, stock:read, historique)
     employe       →  moi:read uniquement
```

Implémentation par dépendances FastAPI (`app/api/deps.py`) :

| Dépendance | Effet si échec |
|------------|----------------|
| `get_current_user` | 401 (token invalide/expiré) |
| `get_current_active_user` | 403 « Compte en attente de validation » |
| `require_roles(*roles)` / `PermDep("perm")` | 403 « Privilèges insuffisants » |

Les routes `/users/*` exigent toutes `SUPERADMIN` (`PermDep("users:read")` / `users:validate` retirés de `ADMIN`).

## Rate limiting

Middleware maison (**pur Starlette, zéro dépendance**) — `app/middleware/rate_limit.py` :

| Route | Limite |
|-------|--------|
| `POST /auth/login/json`, `/employes/inscription` | 5 req / minute / IP |
| `POST /auth/refresh`, `/auth/logout` | 10 req / minute / IP |

Dépassement → **HTTP 429** + header `Retry-After`. Fenêtre glissante en mémoire, clé = IP cliente.

## Headers de sécurité

Ajoutés systématiquement (`app/middleware/security_headers.py`) :

| Header | Valeur | Protection |
|--------|--------|------------|
| `Content-Security-Policy` | `default-src 'self'; frame-ancestors 'none'; …` | XSS, clickjacking |
| `X-Frame-Options` | `DENY` | clickjacking |
| `X-Content-Type-Options` | `nosniff` | mime-sniffing |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | fuite d'URL |
| `Permissions-Policy` | geolocation/micro/camera désactivés | API sensibles navigateur |

> En production HTTPS, décommenter `Strict-Transport-Security` dans le middleware.

## CORS

Liste blanche stricte configurée par environnement (`BACKEND_CORS_ORIGINS`) :
- jamais `allow_origins=["*"]` combiné à `allow_credentials=True`
- méthodes limitées aux verbes utilisés ; headers restreints (`Authorization`, `Content-Type`, `Accept`)
- toute origine inconnue ne reçoit **aucun** header `Access-Control-Allow-Origin`

Vérifié par test : une requête préflight depuis `http://evil-attacker.com` est rejetée.

## Validation des entrées (anti-injection)

Toutes les entrées passent par des schémas Pydantic **avant** tout accès base :
- types et longueurs validés (ex. `reference ≤ 50`, `nom ≤ 150`)
- email validé (`EmailStr`)
- payload non JSON ou champ manquant → **422**, sans toucher la base

Requêtes 100 % paramétrées via SQLAlchemy (aucune concaténation SQL).
Testé avec les payloads classiques (`' OR '1'='1`, `admin'--`, `DROP TABLE`) → 422/401, jamais 500.

## RBAC — contrôle d'accès à 4 rôles

Matrice centralisée unique : `app/core/permissions.py` (API) et `utils/permissions.js`
(frontend, miroir pour l'affichage). Toute route protégée utilise le guard
`PermDep("ressource:action")` — cacher un bouton côté client ne suffit jamais.

| Rôle | Permissions (`app/core/permissions.py`) |
|------|-------------|
| **SUPERADMIN** | `"*"` : tout, présent et futur. **Seul** à `users:read/validate`, création/suppression de comptes et attribution de rôles `admin` |
| **ADMIN** | `dashboard:view`, `referentiels:read`, `stock:read/write`, `employes:read/write`, `affectations:read/write`, `maintenances:read/write`, `historique:read`, `fournisseurs:read/write` — **REST CRUD complet** sur affectations/maintenances, sans `users:*`. Ne peut attribuer que des rôles strictement inférieurs |
| **MANAGER** | lecture seule : `dashboard:view`, `referentiels:read`, `stock:read`, `employes:read`, `historique:read`, `fournisseurs:read` — pas de `stock:write`, `affectations:*`, `maintenances:*` |
| **EMPLOYE** (collaborateur) | `moi:read` uniquement : mes matériels, mes affectations (`/affectations/moi`), mes incidents (`/maintenances/moi`) |

Garde-fous serveur :
- attribution de rôle limitée aux rangs strictement inférieurs (sauf superadmin)
- dernier superadmin actif impossible à désactiver/rétrograder/supprimer
- superadmin exempté des blocages d'auto-modification
- inscription publique (`POST /employes/inscription`) → compte inactif + fiche liée,
  activable uniquement via `/users/{id}/valider` par **superadmin uniquement**

## Secrets et configuration

| Règle | Application |
|-------|-------------|
| Aucun secret dans le code | valeurs par défaut neutres uniquement, surchargées par `env/.env` (dossier centralisé) |
| `env/.env` et `env/.env.production` ignorés par git | `.gitignore` racine |
| `env/.env.example` public | modèle sans vraies valeurs |
| `SECRET_KEY` production | ≥ 128 bits d'entropie, générée via `secrets.token_urlsafe(32)` |
| Comptes par défaut | aucun mot de passe par défaut embarqué ; super admin créé depuis l'environnement uniquement |

## Dépendances

Audités avec `pip-audit` (backend) et `npm audit` (frontend) :
- backend : **0 vulnérabilité connue**
- frontend : vulnérabilités critiques corrigées (Nuxt DevTools RCE, nanoid) ;
  seule reste une faille esbuild **Windows-only** (sans effet sous Linux)

## Journalisation d'audit

Toute écriture sur un équipement produit une entrée `historique` :
auteur, action, valeurs avant/après, horodatage, adresse IP.
Consultable via `GET /api/v1/historique` et par équipement.

## Limitations connues & pistes

- Rate limiting en mémoire : remettre à zéro au redémarrage ; pour du multi-instances,
  passer le compteur dans Redis
- Pas de verrouillage de compte après N échecs (le rate limiting limite déjà la force brute)
- HSTS à activer dès que TLS est en place
