import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import AppLayout from '../layout/AppLayout.vue'

NProgress.configure({ showSpinner: false, speed: 400, minimum: 0.15 })

// 不需要登录即可访问的路由
const PUBLIC_PATHS = new Set(['/login', '/denied', '/public/radar'])

const routes = [
  // ── 公开页面（不在 AppLayout 内） ──
  { path: '/login', component: () => import('../views/login/index.vue') },
  { path: '/denied', component: () => import('../views/denied/index.vue') },
  { path: '/public/radar', component: () => import('../views/radar/public.vue') },

  // ── 需要登录的页面（AppLayout 壳） ──
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', redirect: '/home' },
      { path: 'home', component: () => import('../views/home/index.vue') },
      { path: 'mergeUser', component: () => import('../views/mergeUser/index.vue') },
      { path: 'mmeett', component: () => import('../views/mmeett/index.vue') },
      { path: 'other', component: () => import('../views/other/index.vue') },
      { path: 'soon', component: () => import('../views/soon/index.vue') },
      { path: 'setting', component: () => import('../views/setting/index.vue') },
      { path: 'twCompSet', component: () => import('../views/twCompSet/index.vue') },
      { path: 'jtSaleskits', component: () => import('../views/jtSaleskits/index.vue') },
      { path: 'hwskset', component: () => import('../views/hwskset/index.vue') },
      { path: 'upgradeR3', component: () => import('../views/upgradeR3/index.vue') },
      { path: 'basicComp', component: () => import('../views/basicComp/index.vue') },
      { path: 'baseUpgradeSK', component: () => import('../views/baseUpgradeSK/index.vue') },
      { path: 'updateCI', component: () => import('../views/updateCI/index.vue') },
      { path: 'companyModule', component: () => import('../views/companyModule/index.vue') },
      { path: 'delCP', component: () => import('../views/delCP/index.vue') },
      { path: 'forWeCom', component: () => import('../views/forWeCom/index.vue') },
      { path: 'delBindRelation', component: () => import('../views/delBindRelation/index.vue') },
      { path: 'aboutLogin', component: () => import('../views/aboutLogin/index.vue') },
      { path: 'dzFunction', component: () => import('../views/dzFunction/index.vue') },
      { path: 'batchDeleteClue', component: () => import('../views/batchDeleteClue/index.vue') },
      { path: 'afterSales', component: () => import('../views/afterSales/index.vue') },
      { path: 'miniprogram', component: () => import('../views/miniprogram/index.vue') },
      { path: 'mynote', component: () => import('../views/mynote/index.vue') },
      { path: 'usercenter', component: () => import('../views/usercenter/index.vue') },
      { path: 'easyIC', component: () => import('../views/easyIC/index.vue') },
      { path: 'aitools', component: () => import('../views/aitools/index.vue') },
      { path: 'agent', component: () => import('../views/agent/index.vue') },
      { path: 'radar', component: () => import('../views/radar/index.vue') },
    ],
  },

  // ── 404 兜底（放在最后） ──
  { path: '/:pathMatch(.*)*', component: () => import('../views/notfound/index.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：进度条 + 防重复点击 + 登录检查
let pendingPath = null

router.beforeEach(async (to) => {
  // 防重复点击：相同路径的重复导航直接拦截
  if (pendingPath === to.fullPath) return false
  pendingPath = to.fullPath
  NProgress.start()

  if (PUBLIC_PATHS.has(to.path)) return true

  const { useMenuStore } = await import('../store/menu')
  const menuStore = useMenuStore()

  if (!menuStore.loaded) {
    try {
      await menuStore.fetchMenu()
    } catch {
      return { path: '/login', query: { next: to.fullPath } }
    }
  }
})

router.afterEach(() => {
  pendingPath = null
  NProgress.done()
})

export default router
