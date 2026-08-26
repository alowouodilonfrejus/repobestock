# 1. Présentation

## Qu'est-ce que BeStock ?

**BeStock** est une plateforme web de gestion de stocks et d'inventaire d'équipements.
Elle permet de suivre le parc matériel d'une organisation : quels équipements existent,
où ils se trouvent, dans quel état ils sont, et qui a fait quoi.

## Fonctionnalités

### Gestion du parc
- **Catalogue d'équipements** : création, modification, suppression avec référence unique,
  marque, modèle, numéro de série, date d'acquisition
- **Catégories** : classification (Informatique, Immobilier, Nettoyage…)
- **Statuts** : cycle de vie (Fonctionnel, Défectueux, En maintenance)
- **Emplacements** : localisation physique (bâtiment, étage, salle)

### Suivi et traçabilité
- **Historique automatique** : chaque création / modification / suppression est
  journalisée avec l'auteur, les valeurs avant/après, la date et l'adresse IP
- **Tableau de bord allégé** : actions rapides, 4 stats principales (Articles en stock / Disponibles / Affectés / Maintenance) et activité récente. Le reste est accessible via les pages dédiées
- **Actions rapides** : Ajouter un matériel, Affecter, Ajouter employé, Enregistrer retour — accessibles dès le dashboard
- **Recherche par catégorie** et pagination sur toutes les listes

### Gestion des utilisateurs
- Inscription publique (compte inactif en attente de validation, rôle par défaut `manager` modifiable à la validation)
- RBAC à 4 rôles hiérarchiques : `superadmin` (`*` seul à `users:*`) > `admin` (CRUD affectations/maintenances, sans users) > `manager` (lecture seule) > `employe` (`moi:read`) — matrice centralisée (`app/core/permissions.py` source de vérité, `utils/permissions.js` miroir)
- Inscription : compte créé **inactif**, activé après validation par **superadmin uniquement** (boutons Valider / Rejeter sur `/users`)
- Sidebar dynamique : seuls les menus autorisés par la matrice sont affichés ; les routes et
  l'API restent verrouillées côté serveur (middleware + guards de permission)
- Authentification JWT avec access token + refresh token

## Stack technique

| Couche | Technologie | Version |
|--------|-------------|---------|
| Frontend | Nuxt (Vue 3, Pinia, Tailwind CSS) | 4.x |
| Backend | FastAPI (Python) | 0.141 |
| ORM | SQLAlchemy 2 async | 2.0 |
| Base de données | PostgreSQL | 16 |
| Authentification | PyJWT (HS256) + bcrypt | — |
| Conteneurisation | Docker + Docker Compose | — |

## Captures des concepts clés

```
Utilisateur ──► Frontend Nuxt (:3000) ──► API FastAPI (:8000) ──► PostgreSQL (:5432)
                        │                        │
                   Pinia stores            Journalisation
                  (état global)           table historique
```

Chaque action métier passe par l'API authentifiée par JWT ; toute écriture sur un
équipement génère une entrée dans l'historique consultable depuis l'interface.
