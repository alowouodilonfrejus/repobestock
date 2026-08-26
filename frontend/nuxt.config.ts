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
  routeRules: {
    '/api/**': { proxy: `${process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'}/api/**` }
  },
  vite: {
    server: {
      allowedHosts: process.env.NODE_ENV === 'production' ? [] : true,
      host: '0.0.0.0'
    }
  }
})