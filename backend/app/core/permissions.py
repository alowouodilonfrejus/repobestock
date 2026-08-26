"""Matrice centralisee des permissions RBAC de BeStock.

Roles : SUPERADMIN > ADMIN > MANAGER > EMPLOYE (collaborateur).

- SUPERADMIN : acces complet ("*"), present et futur.
- ADMIN : exploitation quotidienne (stock, categories, employes,
  affectations, maintenance, historique) en REST CRUD complet.
  Ne peut pas gerer les comptes utilisateurs (users:*) ni les superadmins.
- MANAGER : lecture globale uniquement (dashboard, referentiels, stock lecture,
  historique, fournisseurs lecture). Ne gere ni le stock ecriture,
  ni les affectations/maintenances, ni les employes, ni les roles.
- EMPLOYE (collaborateur) : espace personnel uniquement
  (mes materiels, mes affectations, mes retours, mes incidents).

Toute nouvelle fonctionnalite doit declarer sa permission ici puis
utiliser require_permission()/PermDep() dans ses routes.
"""

from app.models.user import UserRole

PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.SUPERADMIN: {"*"},
    UserRole.ADMIN: {
        "dashboard:view",
        "referentiels:read",
        "stock:read",
        "stock:write",
        "employes:read",
        "employes:write",
        "affectations:read",
        "affectations:write",
        "maintenances:read",
        "maintenances:write",
        "historique:read",
        "fournisseurs:read",
        "fournisseurs:write",
    },
    UserRole.MANAGER: {
        "dashboard:view",
        "referentiels:read",
        "stock:read",
        "employes:read",
        "historique:read",
        "fournisseurs:read",
    },
    UserRole.EMPLOYE: {
        "moi:read",
    },
}


def role_has(role: UserRole, permission: str) -> bool:
    perms = PERMISSIONS.get(role, set())
    has = "*" in perms or permission in perms
    # Audit wildcard : toute utilisation de SUPERADMIN:* est logguee cote deps
    return has


def role_permissions(role: UserRole) -> set[str]:
    perms = PERMISSIONS.get(role, set())
    if "*" in perms:
        # SUPERADMIN expose toutes les permissions connues (pour le front)
        all_perms: set[str] = set()
        for p in PERMISSIONS.values():
            all_perms.update(p)
        all_perms.discard("*")
        return all_perms
    return set(perms)


def is_superadmin(role: UserRole) -> bool:
    return "*" in PERMISSIONS.get(role, set())
