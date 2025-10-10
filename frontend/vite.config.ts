import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import sitemap from 'vite-plugin-sitemap';

export default defineConfig(({ command }) => {
  const plugins = [
    react(),
    tailwindcss(),
    sitemap({ hostname: 'https://missbott.online' }),
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
