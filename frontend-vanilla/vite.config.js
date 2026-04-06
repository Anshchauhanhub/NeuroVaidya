import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  base: '/static/dist/',
  build: {
    outDir: resolve(__dirname, '../static/dist'),
    emptyOutDir: true,
    assetsDir: '',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.js'),
      },
      output: {
        entryFileNames: `[name].js`,
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`
      }
    }
  }
})
