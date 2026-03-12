import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward /auth/* to the .NET API so the OAuth2 redirect_uri and cookies work
      '/auth': {
        target: 'https://localhost:7001',
        changeOrigin: true,
        secure: false, // allow self-signed cert in dev
      },
    },
  },
})
