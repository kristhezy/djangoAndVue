import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const DJANGO = 'http://localhost:8001'

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  // 构建产物落在 static/vue/ 下（Django 的 static() 只服务 STATICFILES_DIRS[0]=static/，
  // 输出到 static/ 内才能被 /static/ URL 命中），base 相应指向 /static/vue/
  // dev 模式下 base 用 '/'，避免源码挂在 /static/vue/ 下被 /static 代理规则转发到 Django
  base: command === 'build' ? '/static/vue/' : '/',
  server: {
    port: 5173,
    proxy: {
      '/api': DJANGO,
      '/sv': DJANGO,
      '/ov': DJANGO,
      '/pv': DJANGO,
      '/home': DJANGO,
      '/static': DJANGO,
      '/login': DJANGO,
      '/logout': DJANGO,
    },
  },
  build: {
    outDir: '../static/vue',
    emptyOutDir: true,
  },
}))
