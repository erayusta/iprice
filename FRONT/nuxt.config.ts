// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/color-mode'
  ],
  colorMode: {
    preference: 'light',
    fallback: 'light',
    hid: 'nuxt-color-mode-script',
    globalName: '__NUXT_COLOR_MODE__',
    componentName: 'ColorScheme',
    classPrefix: '',
    classSuffix: '',
    storageKey: 'nuxt-color-mode'
  },
  css: ['~/assets/css/main.css', '~/assets/css/preloader.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8082/api',
      trendyolAiService: process.env.NUXT_PUBLIC_TRENDYOL_AI_SERVICE || 'http://localhost:5002'
    }
  },
  app: {
    baseURL: '/iprice/',
    buildAssetsDir: '/_nuxt/'
  },
  nitro: {
    preset: 'node-server'
  },
  ssr: true,
  experimental: {
    payloadExtraction: false
  }
})
