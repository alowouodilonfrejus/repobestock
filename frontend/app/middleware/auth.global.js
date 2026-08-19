export default defineNuxtRouteMiddleware((to) => {
  if (!import.meta.client) return

  const protectedRoutes = ['/dashboard', '/categories', '/materiel', '/compte', '/historique', '/equipements', '/users']

  if (protectedRoutes.some((path) => to.path.startsWith(path))) {
    const authStore = useAuthStore()
    if (!authStore.isAuthenticated) {
      return navigateTo('/connexion')
    }
  }
})