import Aura from '@primevue/themes/aura';

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false, // Build as SPA

  nitro: {
    preset: 'cloudflare-pages'
  },

  runtimeConfig: {
    tursoUrl: process.env.NUXT_TURSO_URL || '',
    tursoToken: process.env.NUXT_TURSO_TOKEN || '',
    jwtSecret: process.env.NUXT_JWT_SECRET || 'chamsoc-dev-secret-2026',
    initSecret: process.env.NUXT_INIT_SECRET || 'changeme-in-production'
  },

  modules: [
    '@primevue/nuxt-module',
    '@nuxtjs/tailwindcss'
  ],

  css: [
    'primeicons/primeicons.css',
    '~/assets/layout/layout.scss'
  ],

  primevue: {
    options: {
      theme: {
        preset: Aura,
        options: {
          darkModeSelector: '.app-dark'
        }
      }
    },
    components: {
      include: '*'
    },
    directives: {
      include: ['Tooltip']
    }
  },

  tailwindcss: {
    configPath: 'tailwind.config.js'
  }
})
