export default defineNuxtConfig({
  compatibilityDate: '2026-10-26',
  telemetry: false,
  devtools: { enabled: false },
  routeRules: { '/account': { ssr: false, prerender: true } },
  nitro: { prerender: { routes: ['/', '/games/fixture', '/account'], crawlLinks: false } }
})
