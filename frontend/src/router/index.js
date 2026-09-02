import { createRouter, createWebHistory } from 'vue-router'
import LegacyIframe from '../views/LegacyIframe.vue'
import AppLayout from '../layout/AppLayout.vue'

// 迁移开关：迁完一页，把对应路径改成 import 的 Vue 组件即可。
const migrated = {
  mergeUser: () => import('../views/mergeUser/index.vue'),
  other: () => import('../views/other/index.vue'),
  mynote: () => import('../views/mynote/index.vue'),
  delCP: () => import('../views/delCP/index.vue'),
  batchDeleteClue: () => import('../views/batchDeleteClue/index.vue'),
  forWeCom: () => import('../views/forWeCom/index.vue'),
  delBindRelation: () => import('../views/delBindRelation/index.vue'),
  aboutLogin: () => import('../views/aboutLogin/index.vue'),
  dzFunction: () => import('../views/dzFunction/index.vue'),
  jtSaleskits: () => import('../views/jtSaleskits/index.vue'),
  hwskset: () => import('../views/hwskset/index.vue'),
  upgradeR3: () => import('../views/upgradeR3/index.vue'),
  basicComp: () => import('../views/basicComp/index.vue'),
  baseUpgradeSK: () => import('../views/baseUpgradeSK/index.vue'),
  companyModule: () => import('../views/companyModule/index.vue'),
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
      { path: 'other', component: migrated.other || LegacyIframe },
      legacy('/ov/soonConfig'),
      legacy('/ov/setting'),
      legacy('/ov/twCompSet'),
      { path: 'jtSaleskits', component: migrated.jtSaleskits || LegacyIframe },
      { path: 'hwskset', component: migrated.hwskset || LegacyIframe },
      { path: 'upgradeR3', component: migrated.upgradeR3 || LegacyIframe },
      { path: 'basicComp', component: migrated.basicComp || LegacyIframe },
      { path: 'baseUpgradeSK', component: migrated.baseUpgradeSK || LegacyIframe },
      legacy('/sv/updateCT'),
      { path: 'companyModule', component: migrated.companyModule || LegacyIframe },
      { path: 'delCP', component: migrated.delCP || LegacyIframe },
      { path: 'forWeCom', component: migrated.forWeCom || LegacyIframe },
      { path: 'delBindRelation', component: migrated.delBindRelation || LegacyIframe },
      { path: 'aboutLogin', component: migrated.aboutLogin || LegacyIframe },
      { path: 'dzFunction', component: migrated.dzFunction || LegacyIframe },
      { path: 'batchDeleteClue', component: migrated.batchDeleteClue || LegacyIframe },
      legacy('/sv/afterSales'),
      legacy('/sv/miniprogram'),
      { path: 'mynote', component: migrated.mynote || LegacyIframe },
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
