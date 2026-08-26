import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { hasPermission, roleHas } from '~/utils/permissions'

export const useRole = () => {
  const authStore = useAuthStore()

  const role = computed(() => authStore.user?.role || null)
  const isEmploye = computed(() => role.value === 'employe')
  const isManager = computed(() => ['manager', 'admin', 'superadmin'].includes(role.value))
  const isAdmin = computed(() => ['admin', 'superadmin'].includes(role.value))
  const isSuperAdmin = computed(() => role.value === 'superadmin')
  const canWrite = computed(() => isAdmin.value)
  // Priorite : permissions serveur (source de verite), fallback matrice locale
  const can = (permission) => {
    if (authStore.permissions && authStore.permissions.length > 0) {
      return hasPermission(authStore.permissions, permission)
    }
    return roleHas(role.value, permission)
  }

  return { role, isEmploye, isManager, isAdmin, isSuperAdmin, canWrite, can }
}

