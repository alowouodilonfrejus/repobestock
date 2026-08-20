import axios from 'axios'

const apiBase = import.meta.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: apiBase,
  headers: {
    'Content-Type': 'application/json',
  },
})

const NO_REFRESH_URLS = ['/auth/login', '/auth/register', '/auth/refresh', '/auth/logout']

let refreshPromise = null

function clearSession() {
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem('bestock_token')
    localStorage.removeItem('bestock_refresh')
    localStorage.removeItem('bestock_user')
  }
  if (typeof window !== 'undefined' && window.location.pathname !== '/connexion') {
    window.location.href = '/connexion'
  }
}

async function refreshTokens() {
  if (refreshPromise) return refreshPromise
  const refreshToken = localStorage.getItem('bestock_refresh')
  if (!refreshToken) {
    refreshPromise = Promise.reject(new Error('No refresh token'))
  } else {
    refreshPromise = api
      .post('/auth/refresh', { refresh_token: refreshToken })
      .then(({ data }) => {
        localStorage.setItem('bestock_token', data.access_token)
        localStorage.setItem('bestock_refresh', data.refresh_token)
        return data.access_token
      })
  }
  refreshPromise = refreshPromise.finally(() => {
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
        clearSession()
        return Promise.reject(refreshError)
      }
    }

    if (error.response?.status === 401) {
      clearSession()
    }

    return Promise.reject(error)
  }
)

export default api