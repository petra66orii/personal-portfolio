import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ command }) => {
  const plugins = [
    react(),
    tailwindcss(),
  ];

  if (command === 'serve') {
    // --- DEVELOPMENT ---
    return {
      plugins,
      base: '/',
      server: {
        proxy: {
          '/api': {
            target: 'http://localhost:8000',
            changeOrigin: true,
            secure: false,
          },
        },
      },
    }
  } else {
    // --- PRODUCTION BUILD ---
    return {
      plugins,
      base: '/static/',
    }
  }
})
