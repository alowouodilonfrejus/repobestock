export default defineNuxtRouteMiddleware((to) => {
  if (!import.meta.client) return

  const protectedRoutes = ['/dashboard', '/categories', '/materiel', '/compte', '/historique', '/equipements', '/users', '/employes', '/affectations', '/maintenance']

  const needsAuth = protectedRoutes.some((path) => to.path.startsWith(path))
  const isStaffRoute = ['/dashboard', '/categories', '/materiel', '/historique', '/equipements', '/employes', '/affectations', '/maintenance'].some((path) => to.path.startsWith(path))
  const isAdminRoute = to.path.startsWith('/users')

  const authStore = useAuthStore()
  if (needsAuth && !authStore.isAuthenticated) {
    return navigateTo('/connexion')
  }

  const role = authStore.user?.role
  if (!role) return
  // Source de verite : permissions serveur si disponibles, sinon fallback role
  const can = (perm) => {
    if (authStore.permissions && authStore.permissions.length > 0) {
      return authStore.permissions.includes('*') || authStore.permissions.includes(perm)
    }
    // fallback legacy (aligne sur permissions.py: ADMIN sans users, MANAGER lecture seule)
    const map = { 'stock:write': ['admin','superadmin'], 'affectations:write': ['admin','superadmin'], 'maintenances:write': ['admin','superadmin'], 'users:read': ['superadmin'] }
    return (map[perm] || []).includes(role)
  }

  if (role === 'employe' && isStaffRoute) {
    return navigateTo('/mes-materiels')
  }
  if (isAdminRoute && !can('users:read')) {
    return navigateTo('/mes-materiels')
  }
  if (to.path.startsWith('/materiel/nouveau') && !can('stock:write')) {
    return navigateTo('/categories')
  }
  if (to.path.startsWith('/affectations/nouvelle') && !can('affectations:write')) {
    return navigateTo('/affectations')
  }
})
