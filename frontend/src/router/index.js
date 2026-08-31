import { createRouter, createWebHistory } from 'vue-router'
import LegacyIframe from '../views/LegacyIframe.vue'
import AppLayout from '../layout/AppLayout.vue'

// 迁移开关：迁完一页，把对应路径改成 import 的 Vue 组件即可。
const migrated = {
  mergeUser: () => import('../views/mergeUser/index.vue'),
}

// 嵌套子路由：去掉前导斜杠作为 AppLayout（path:'/'）的 children
function legacy(path) {
  return { path: path.replace(/^\//, ''), name: path, component: LegacyIframe }
}

const routes = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', component: LegacyIframe },
      { path: 'mergeUser', component: migrated.mergeUser || LegacyIframe },
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
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
