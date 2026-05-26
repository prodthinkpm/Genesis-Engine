export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    "@pinia/nuxt",
    "@vueuse/nuxt",
    "@nuxtjs/tailwindcss",
  ],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
      wsBase: process.env.NUXT_PUBLIC_WS_BASE || "ws://localhost:8000",
    },
  },

  tailwindcss: {
    config: {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            genesis: {
              bg: "#0a0e1a",
              card: "#111827",
              border: "#1f2937",
              accent: "#f59e0b",
              accent2: "#6366f1",
              text: "#e5e7eb",
              muted: "#6b7280",
              online: "#10b981",
              proxy: "#f59e0b",
              offline: "#6b7280",
            },
          },
        },
      },
    },
  },

  typescript: {
    strict: true,
  },
});
