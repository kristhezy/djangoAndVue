<template>
  <div class="layout">
    <HeaderBar />
    <div class="body">
      <SidebarMenu />
      <main class="content">
        <router-view />
      </main>
    </div>
    <AuditPollingFloat />
  </div>
</template>

<script setup>
import HeaderBar from './HeaderBar.vue'
import SidebarMenu from './SidebarMenu.vue'
import AuditPollingFloat from '../components/AuditPollingFloat.vue'
import { useMenuStore } from '../store/menu'

const menuStore = useMenuStore()
// 菜单数据由 router beforeEach 守卫预加载，此处兜底确保
if (!menuStore.loaded) {
  menuStore.fetchMenu()
}
</script>

<style scoped>
.layout { height: 100vh; display: flex; flex-direction: column; }
.body { flex: 1; display: flex; overflow: hidden; }
.content { flex: 1; overflow: hidden; background: var(--bg-page); }
</style>
