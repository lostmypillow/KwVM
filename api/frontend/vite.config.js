import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(),   tailwindcss(),],
  build: {
    outDir: "../backend/public", // Output to backend/public
    emptyOutDir: true, // Delete existing files before building
  },
  base: "/dash",
  server: {
    proxy: {
      "/vm/": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
})
