import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { TanStackRouterVite } from '@tanstack/router-vite-plugin'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    TanStackRouterVite(),
  ],
  envDir: resolve(__dirname, '..'), // Use parent directory for .env files
  server: {
    port: 5173,
    strictPort: true, // Fail if port is occupied instead of using fallback
    host: true,
  },
})
