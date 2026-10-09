// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: process.env.NODE_ENV !== 'production' },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api/v1',
    },
  },
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxt/image'
  ],
  icon: {
    serverBundle: {
      collections: ['heroicons', 'mdi']
    },
    clientBundle: {
      scan: true,
      collections: ['heroicons', 'mdi']
    }
  },
  routeRules: (() => {
    const apiBase = process.env.NUXT_PUBLIC_API_BASE
    if (apiBase) {
      return { '/api/**': { proxy: `${apiBase}/api/**` } }
    }
    // Dev uniquement : en production sans base explicite, ne jamais
    // proxifier vers localhost:8000 (conteneur/cible inexistante en prod)
    if (process.env.NODE_ENV !== 'production') {
      return { '/api/**': { proxy: 'http://localhost:8000/api/**' } }
    }
    return {}
  })(),
  vite: {
    server: {
      allowedHosts: process.env.NODE_ENV === 'production' ? [] : true,
      host: '0.0.0.0'
    }
  }
})