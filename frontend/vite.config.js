// vite.config.js (The Absolute Final Configuration Fix)

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [
    // 1. Load the standard React plugin
    react(), 
  ],
  
  // CRITICAL DEFINITIVE FIX: Forcing the ESBuild Loader during dependency scanning.
  // This targets the exact process that is failing (dependency scanning/optimization).
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        // This is the instruction the error message requested: force all .js files to be parsed as JSX
        '.js': 'jsx' 
      },
    },
  },

  // NOTE: If the above fails, your version of Vite/esbuild might require a simple, direct esbuild block:
  // esbuild: {
  //   loader: 'jsx',
  //   include: /.\/src\/.*\.js$/, 
  //   exclude: [],
  // },
  
  // Define the root and build settings
  root: './',
  publicDir: 'public',
  server: {
    port: 3000, 
  },
  build: {
    outDir: 'dist', 
    rollupOptions: {
      // Ensure the input is correctly set to the .js extension
      input: './src/index.js', 
    },
  },
});
