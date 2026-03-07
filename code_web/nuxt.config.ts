import Aura from '@primevue/themes/aura';

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false, // Build as SPA

  nitro: {
    preset: 'cloudflare-pages'
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
  },

  vite: {
    server: {
      allowedHosts: true // Allow trycloudflare.com tunnel URLs
    }
  }
})
