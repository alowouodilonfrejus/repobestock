// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
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
    '/api/**': { proxy: 'http://localhost:8000/api/**' }
  },
  vite: {
    server: {
      allowedHosts: true,
      host: '0.0.0.0'
    }
  }
})