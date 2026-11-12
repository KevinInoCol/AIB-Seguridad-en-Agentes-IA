import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// El frontend llama a /api/* y Vite lo reenvía al backend FastAPI.
// Así no hace falta CORS en desarrollo.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5180,
    strictPort: true, // si 5180 está ocupado, falla en vez de saltar a otro puerto
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
