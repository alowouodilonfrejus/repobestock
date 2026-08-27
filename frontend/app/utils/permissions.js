
export const ROLE_PERMISSIONS = {
  superadmin: ['*'],
  admin: [
    'dashboard:view',
    'referentiels:read',
    'stock:read',
    'stock:write',
    'employes:read',
    'employes:write',
    'affectations:read',
    'affectations:write',
    'maintenances:read',
    'maintenances:write',
    'historique:read',
    'fournisseurs:read',
    'fournisseurs:write',
  ],
  manager: [
    'dashboard:view',
    'referentiels:read',
    'stock:read',
    'employes:read',
    'historique:read',
    'fournisseurs:read',
  ],
  employe: ['moi:read'],
}

export function roleHas(role, permission) {
  const perms = ROLE_PERMISSIONS[role] || []
  return perms.includes('*') || perms.includes(permission)
}

// Nouveau helper : verifie permissions serveur (authStore.permissions)
export function hasPermission(permissions, permission) {
  if (!permissions) return false
  return permissions.includes('*') || permissions.includes(permission)
}
