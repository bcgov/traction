import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// So that when we run this FE in dev mode separately (not served by the node api)
// it'll call the api properly for config and backend calls (consider make env var for API)
// https://vitejs.dev/config/server-options.html#server-proxy
const proxyObject = {
  target: 'http://localhost:8080',
  ws: true,
  changeOrigin: true
};

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': proxyObject,
      '/config': proxyObject
    }
  }
})
