import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";  

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),          
  ],
  build: {
    outDir: "dist-admin",
    emptyOutDir: true,
    cssCodeSplit: false, 
    rollupOptions: {
      input: "src/admin-entry.tsx",
      output: {
        format: "iife",
        entryFileNames: "audit-dashboard.bundle.js",
        assetFileNames: "audit-dashboard.[ext]",
        manualChunks: undefined,
        inlineDynamicImports: true,
      },
    },
  },
});
