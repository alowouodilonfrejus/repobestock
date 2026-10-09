import { useAuthStore } from '~/stores/auth'

export default defineNuxtPlugin(async (nuxtApp) => {
  const authStore = useAuthStore()
  // Attendu : la validation de session (cookies httpOnly) doit etre faite
  // avant la navigation initiale, sinon le middleware auth.global verrait
  // un visiteur non connecte
  await authStore.hydrate()
})