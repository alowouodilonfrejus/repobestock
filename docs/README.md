# Documentation BeStock

Bienvenue dans la documentation complète de **BeStock**, la plateforme de gestion de stocks et d'inventaire.

## Sommaire

| # | Document | Contenu |
|---|----------|---------|
| 1 | [Présentation](01-presentation.md) | Le projet, les fonctionnalités, la stack technique |
| 2 | [Architecture](02-architecture.md) | Vue d'ensemble, architecture en couches, arborescence |
| 3 | [Installation](03-installation.md) | Démarrage développement, déploiement production |
| 4 | [API REST](04-api.md) | Référence complète des endpoints (requêtes/réponses) |
| 5 | [Modèles de données](05-modeles-donnees.md) | Schéma de base de données, tables, relations |
| 6 | [Sécurité](06-securite.md) | Authentification, autorisations, protections |
| 7 | [Frontend](07-frontend.md) | Pages Nuxt, stores Pinia, client API |

## Liens rapides

- API Swagger (dev) : http://localhost:8000/docs
- OpenAPI JSON : http://localhost:8000/api/v1/openapi.json
- README principal : [../README.md](../README.md)

## Public visé

| Rôle | Documents recommandés |
|------|----------------------|
| Utilisateur | 01, 04 |
| Développeur backend | 02, 04, 05, 06 |
| Développeur frontend | 02, 04, 07 |
| DevOps | 03, 06 |

## Sécurité & RBAC — vérifié

Le système d'autorisation a été **testé concrètement** (août 2026) :

- **Backend** : `/api/v1/users` renvoie **403 Forbidden** pour les rôles `ADMIN`, `MANAGER`, `EMPLOYE`
- **Frontend** : Le lien "Utilisateurs" n'apparaît que pour le rôle `SUPERADMIN` (via `can('users:read')`)
- **Middleware** : Toute tentative directe `/users` redirige vers `/mes-materiels` si le rôle n'a pas la permission

> 📖 Documentation détaillée : voir [`06-securite.md`](06-securite.md) pour la matrice RBAC complète, les dépendances FastAPI et les tests effectués.
