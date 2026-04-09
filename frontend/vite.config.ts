import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  if (process.env.VERCEL && !env.VITE_API_URL?.trim()) {
    throw new Error('VITE_API_URL must be set in Vercel before deploying the frontend.')
  }

  return {
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
  }
})
