import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/auth/google': 'http://localhost:8000',
      '/auth/me': 'http://localhost:8000',
      '/auth/set-role': 'http://localhost:8000',
      '/groups': 'http://localhost:8000',
      '/chat': 'http://localhost:8000'
    }
  }
})
