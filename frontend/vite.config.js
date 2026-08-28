import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const DJANGO = 'http://localhost:8001'

export default defineConfig({
  plugins: [vue()],
  // 构建产物落在 static/vue/ 下（Django 的 static() 只服务 STATICFILES_DIRS[0]=static/，
  // 输出到 static/ 内才能被 /static/ URL 命中），base 相应指向 /static/vue/
  base: '/static/vue/',
  server: {
    port: 5173,
    proxy: {
      '/api': DJANGO,
      '/sv': DJANGO,
      '/ov': DJANGO,
      '/pv': DJANGO,
      '/static': DJANGO,
      '/login': DJANGO,
      '/logout': DJANGO,
    },
  },
  build: {
    outDir: '../static/vue',
    emptyOutDir: true,
  },
})
