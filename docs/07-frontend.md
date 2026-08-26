# 7. Frontend (Nuxt 4)

## Stack

| Élément | Technologie |
|---------|-------------|
| Framework | Nuxt 4 (Vue 3, SSR) |
| État global | Pinia (`@pinia/nuxt`) |
| Styles | Tailwind CSS (`@nuxtjs/tailwindcss`) |
| Requêtes HTTP | axios (client unique `app/utils/api.js`) |
| Icônes | `@nuxt/icon` — collections heroicons + mdi **bundleées localement** (aucun appel réseau au runtime) |
| Typographie | `@nuxt/fonts` |

## Pages

| Route | Fichier | Accès | Rôle |
|-------|---------|-------|------|
| `/` | `pages/index.vue` | public | Landing page |
| `/connexion` | `pages/connexion.vue` | public | Login (email + mot de passe) |
| `/inscription` | `pages/inscription.vue` | public | Création de compte |
| `/dashboard` | `pages/dashboard.vue` | 🔒 | **Centre de contrôle** : 4 stats principales, indicateurs secondaires, analyse du stock, alertes, affectations et activité récentes (`GET /equipements/stats` + `/historique`) |
| `/materiel/nouveau` | `pages/materiel/nouveau.vue` | 🔒 | Formulaire de création d'équipement |
| `/equipements/[id]` | `pages/equipements/[id].vue` | 🔒 | Fiche équipement + historique lié |
| `/categories` | `pages/categories/index.vue` | 🔒 | Liste des catégories |
| `/categories/[id]` | `pages/categories/[id].vue` | 🔒 | Équipements d'une catégorie |
| `/employes` | `pages/employes/index.vue` | 🔒 | Liste et création d'employés |
| `/affectations` | `pages/affectations/index.vue` | 🔒 | Liste, création et retours de matériel |
| `/maintenance` | `pages/maintenance.vue` | 🔒 | Matériels en maintenance et clôtures |
| `/historique` | `pages/historique.vue` | 🔒 | Journal global (auteur, avant/après) |
| `/users` | `pages/users/index.vue` | 🔒 **superadmin seul** (`users:read`) | Gestion des comptes (admin n'y a plus accès) |
| `/compte` | `pages/compte.vue` | 🔒 | Profil personnel |

> 🔒 = protégé par le middleware global.

## Middleware et plugins

### `middleware/auth.global.js`
Garde exécutée sur **toutes** les navigations (source de vérité `authStore.permissions` + fallback `permissions.js`) :
- routes protégées + pas de session → redirection `/connexion`
- rôle `employe` sur une route staff (dashboard, stock, collaborateurs…) → `/mes-materiels`
- routes `/users` réservées **superadmin seul** (`users:read`) — admin redirigé vers `/mes-materiels`
- écriture affectations/maintenance (`/affectations/nouvelle`, `POST /maintenances`) réservée **superadmin/admin** (`affectations:write`, `maintenances:write`) — manager redirigé
- `/materiel/nouveau` réservé **superadmin/admin** (`stock:write`)

### RBAC côté affichage — `utils/permissions.js` + `composables/useRole.js`
Source de vérité backend `app/core/permissions.py` exposée via `GET /auth/me {permissions}`. Fallback offline `utils/permissions.js` (admin sans `users:*`, manager lecture seule). `useRole()` expose `role`, `isEmploye`, `isAdmin`, `canWrite` et `can("perm")` qui privilégie `authStore.permissions`. La sidebar `layouts/dashboard.vue:192` filtre `menuPrincipal` par `can(perm)` et `menuUtilisateurs` par `users:read` (superadmin seul) ; `QuickActions.vue:3` masque `stock:write` / `affectations:write`. L'autorité reste côté API : toute requête non autorisée → 403.

### `plugins/auth.client.js`
Au chargement côté client : restaure la session depuis le stockage local puis
tente un `refresh` silencieux si l'access token est expiré.

## Stores Pinia

Chaque store suit le même modèle avec **cache mémoire** :

```js
// pseudo-structure commune
state: { items: [], _loaded: false }
actions: {
  async fetch(force = false) {        // skippe l'appel si déjà chargé
    if (this._loaded && !force) return
    this.items = await api.get('...')
    this._loaded = true
  }
}
```

| Store | Endpoint(s) | Particularité |
|-------|-------------|---------------|
| `auth.js` | `/auth/login/json`, `/auth/me`, refresh/logout | conserve tokens, expose l'utilisateur courant |
| `categories.js` | `/categories`, `/statuts`, `/emplacements` | cache long (référentiel stable), `pickIcon`, `fieldsFor()` |
| `equipements.js` | `/equipements`, `/equipements/stats` | `stats` = `{total, maintenance, disponibles, affectes, endommages, perdus, hors_service, affectations_actives, retours_total, affectations_recentes, recent}` ; invalidation `_loadedStats` après CUD |
| `affectations.js` | `/affectations` | `affectations_recentes` utilisées sur dashboard |
| `maintenances.js` | `/maintenances` | `total` pour alertes |
| `employes.js` | `/employes` | liste employés |
| `historique.js` | `/historique`, `/equipements/{id}/historique` | alimente `ActivityFeed` (6 derniers) |
| `users.js` | `/users` (CRUD) | réservé superadmin |

### Invalidation automatique
Après toute création/modification/suppression, le cache concerné est marqué
obsolète pour se recharger au prochain affichage (données toujours fraîches sans polling).

## Client API — `utils/api.js`

Point central de toutes les requêtes (fix `NUXT_E1001` : `getApiBase()` ne passe plus `useRuntimeConfig()` au top-level SSR — `if(import.meta.server) return '/api/v1'`) :

- base URL : `/api/v1` (proxy `nuxt.config.ts:22` → `http://localhost:8000/api/**`) ou `NUXT_PUBLIC_API_BASE`
- injection automatique du header `Authorization: Bearer …`
- **intercepteur 401** : tente un `POST /auth/refresh`, rejoue la requête initiale ;
  si le refresh échoue → `clearSession()` (supprime `bestock_permissions` aussi) et redirection `/connexion`
- `useRoute/useRouter` désormais auto-importés Nuxt (plus d'import `vue-router`)

## Dashboard — centre de contrôle (2026-08-23)

`pages/dashboard.vue` orchestré autour de 6 briques réutilisables dans `components/dashboard/` :

| Composant | Rôle | Données | États |
|-----------|------|---------|-------|
| `DashboardStatCard.vue` | Carte stat principale (chiffre dominant 28px, icône colorée, lien `Voir`) | `stats.total / disponibles / affectes / maintenance` | `variant` default/success/info/warning gère `bg/text/dot` |
| `QuickActions.vue` | 4 raccourcis → routes existantes | — | `Ajouter matériel` (primary `#0f2a4a`), autres `white/border` |
| `StockOverview.vue` | Répartition visuelle sans librairie lourde | `stats` (6 segments) | Barres hauteur `value/max`, pile proportionnelle `pct` ; couleurs : Disponible `#10b981`, Affecté `#0ea5e9`, Maintenance `#f59e0b`, Endommagé `#f97316`, Perdu `#ef4444`, Hors service `#64748b` |
| `AlertsPanel.vue` | Éléments à traiter | `stats.maintenance/endommages/perdus/hors_service` | `totalAlerts` → badge, empty `Aucune alerte` |
| `ActivityFeed.vue` | 6 dernières entrées `historique` | `historique` store + `equipements` pour nom | skeletons, badges création/modification/suppression, empty |
| `MaterialTable.vue` | 8 matériels récents | `equipements.recentMaterials` + `categories`/`statuts` | `statusMeta()` mappe nom → `cls/dot`, empty CTA |

Hiérarchie : `Dashboard` > `Vue d'ensemble…` > `QuickActions` > `4 stats` > `4 indicateurs compacts` > `StockOverview (col-span-2) + Alerts` > `Affectations récentes + ActivityFeed (col-span-2)` > `MaterialTable`. Tous les liens (`Voir la maintenance →`, `Affecter un matériel`…) pointent vers des routes réelles. Responsive `grid-cols-1 sm:grid-cols-2 xl:grid-cols-4`, skeletons et empty states partout.

## Layouts

- `layouts/default.vue` : navigation publique (landing, connexion…)
- `layouts/dashboard.vue` : **coquille SaaS** — sidebar `w-[264px]` bg `#0f2a4a` groupée (Principal : Accueil/Dashboard/Catégories/Employés/Affectations/Maintenance/Historique ; Administration : Utilisateurs/Paramètres) + CTA `+ Ajouter un matériel` + bloc utilisateur (initiales, email) ; header sticky `h-[64px]` `bg-white/80 backdrop-blur` avec breadcrumbs (`BeStock / dashboard`), recherche globale `→ /categories?q=`, notifications (dot si `stats.maintenance>0`), profil `rounded-full`

## Icônes SVG

Configurées dans `nuxt.config.ts` :

```ts
icon: {
  serverBundle: { collections: ['heroicons', 'mdi'] },   // rendu SSR
  clientBundle: { scan: true }                           // détection auto + embarquement
}
```

Usage dans les composants : `<Icon name="heroicons:home" class="h-5 w-5" />`.
Les icônes détectées sont embarquées dans le bundle → zéro appel réseau au runtime.

## Lancer / builder

```bash
npm run dev        # développement (http://localhost:3000)
npm run build      # build production SSR
npm run generate   # pré-rendu statique
npm run preview    # sert le build
```
