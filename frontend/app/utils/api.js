import axios from 'axios'

function getApiBase() {
  try {
    if (typeof useRuntimeConfig === 'function') {
      const cfg = useRuntimeConfig()
      if (cfg?.public?.apiBase) return cfg.public.apiBase
    }
  } catch {}
  if (typeof process !== 'undefined' && process.env?.NUXT_PUBLIC_API_BASE) return process.env.NUXT_PUBLIC_API_BASE
  return import.meta.env?.NUXT_PUBLIC_API_BASE || '/api/v1'
}

// Les tokens vivent en cookies httpOnly (fixes par le backend) :
// withCredentials est indispensable pour les envoyer/recuperer en cross-origin
const api = axios.create({
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

const NO_REFRESH_URLS = ['/auth/login', '/auth/register', '/auth/refresh', '/auth/logout']

let refreshPromise = null

function clearSession() {
  if (typeof localStorage !== 'undefined') {
    try {
      // Nettoyage des anciennes cles (avant migration vers les cookies)
      localStorage.removeItem('bestock_token')
      localStorage.removeItem('bestock_refresh')
      localStorage.removeItem('bestock_session')
      localStorage.removeItem('bestock_user')
      localStorage.removeItem('bestock_permissions')
    } catch {}
  }
  if (typeof window !== 'undefined' && window.location.pathname !== '/connexion') {
    window.location.href = '/connexion'
  }
}

async function refreshTokens() {
  if (refreshPromise) return refreshPromise
  // Refresh via cookie httpOnly : aucun jeton expose en JS
  refreshPromise = api
    .post('/auth/refresh', {})
    .then(() => true)
    .catch((e) => {
      // Token invalide/expire -> ne pas boucler, propager pour clearSession
      throw e
    })
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}

api.interceptors.request.use((config) => {
  config.baseURL = getApiBase()
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const isAuthUrl = NO_REFRESH_URLS.some((path) => original?.url?.includes(path))

    if (error.response?.status === 401 && original && !original._retry && !isAuthUrl) {
      original._retry = true
      try {
        await refreshTokens()
        // Les cookies sont renvoyes automatiquement par le navigateur
        return api(original)
      } catch (refreshError) {
        // Echec refresh -> deconnecter, mais ne pas boucler
        clearSession()
        return Promise.reject(refreshError)
      }
    }

    // Ne deconnecter que si ce n'est pas une requete d'auth (login echoue != session expiree)
    if (error.response?.status === 401 && !isAuthUrl) {
      clearSession()
    }

    return Promise.reject(error)
  }
)

export default api
