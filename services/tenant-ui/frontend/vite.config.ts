import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite';

// So that when we run this FE in dev mode separately (not served by the node api)
// it'll call the api properly for config and backend calls (consider make env var for API)
// https://vitejs.dev/config/server-options.html#server-proxy
const proxyObject = {
  target: 'http://localhost:8080',
  ws: true,
  changeOrigin: true,
};

// https://vitetest.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VueI18nPlugin({
      include: path.resolve(__dirname, './src/plugins/i18n/locales/**'),
      strictMessage: false,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/logStream': {
        target: 'ws://localhost:8080',
        ws: true,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/logStream/, ''),
      },
      '/api': proxyObject,
      '/config': proxyObject,
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/assets/variables.scss" as *;`,
        api: 'modern-compiler',
      },
    },
  },
  test: {
    globals: true,
    setupFiles: ['/test/setupGlobalMocks.ts', '/test/setupApi.ts'],
    environment: 'jsdom',
  },
});
