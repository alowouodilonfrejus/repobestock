import axios from 'axios'

function getApiBase() {
  // SSR: ne jamais appeler useRuntimeConfig au top-level (NUXT_E1001)
  // useRuntimeConfig() n'est valide que dans setup/plugin/middleware
  if (import.meta.server) return '/api/v1'
  try {
    if (typeof useRuntimeConfig === 'function') {
      const cfg = useRuntimeConfig()
      if (cfg?.public?.apiBase) return cfg.public.apiBase
    }
  } catch {}
  return import.meta.env.NUXT_PUBLIC_API_BASE || '/api/v1'
}

const api = axios.create({
  baseURL: getApiBase(),
  headers: {
    'Content-Type': 'application/json',
  },
})

const NO_REFRESH_URLS = ['/auth/login', '/auth/register', '/auth/refresh', '/auth/logout']

let refreshPromise = null

function clearSession() {
  if (typeof localStorage !== 'undefined') {
    try {
      localStorage.removeItem('bestock_token')
      localStorage.removeItem('bestock_refresh')
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
  const refreshToken = typeof localStorage !== 'undefined' ? localStorage.getItem('bestock_refresh') : null
  if (!refreshToken) {
    return Promise.reject(new Error('No refresh token'))
  }
  refreshPromise = api
    .post('/auth/refresh', { refresh_token: refreshToken })
    .then(({ data }) => {
      localStorage.setItem('bestock_token', data.access_token)
      localStorage.setItem('bestock_refresh', data.refresh_token)
      return data.access_token
    })
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
  if (typeof localStorage !== 'undefined') {
    const token = localStorage.getItem('bestock_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
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
        const newToken = await refreshTokens()
        original.headers.Authorization = `Bearer ${newToken}`
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