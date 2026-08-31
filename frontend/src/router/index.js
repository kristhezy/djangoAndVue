import { createRouter, createWebHistory } from 'vue-router'
import LegacyIframe from '../views/LegacyIframe.vue'

// 迁移开关：迁完一页，把对应路径改成 import 的 Vue 组件即可。
const migrated = {
  // mergeUser: () => import('../views/mergeUser/index.vue'),  // Task 8 启用
}

// 本阶段（Task 6）无壳，平铺路由，全部绝对路径；Task 7 引入 AppLayout 后会重写为嵌套结构。
function legacy(path) {
  return { path, name: path, component: LegacyIframe }
}

const routes = [
  // 默认页：先指向旧首页（iframe）
  { path: '/', component: LegacyIframe },
  // 试点页（暂走 iframe，Task 8 切换）
  { path: '/mergeUser', component: migrated.mergeUser || LegacyIframe },
  // 未迁移页统一走 LegacyIframe（保留旧 URL 语义）
  legacy('/home'),
  legacy('/ov/mmeettopen'),
  legacy('/pv/other'),
  legacy('/ov/soonConfig'),
  legacy('/ov/setting'),
  legacy('/ov/twCompSet'),
  legacy('/sv/jtSaleskits'),
  legacy('/sv/hwskset'),
  legacy('/sv/upgradeR3'),
  legacy('/sv/basicComp'),
  legacy('/sv/baseUpgradeSK'),
  legacy('/sv/updateCT'),
  legacy('/sv/companyModule'),
  legacy('/sv/delCP'),
  legacy('/sv/forWeCom'),
  legacy('/sv/delBindRelation'),
  legacy('/sv/queryLoginCode'),
  legacy('/sv/dzFunction'),
  legacy('/sv/batchDeleteClue'),
  legacy('/sv/afterSales'),
  legacy('/sv/miniprogram'),
  legacy('/pv/mynote'),
  legacy('/pv/usercenter'),
  legacy('/pv/easyIC'),
  legacy('/pv/aitools'),
  legacy('/pv/agent'),
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
