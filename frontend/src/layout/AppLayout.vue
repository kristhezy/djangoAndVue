<template>
  <div class="layout">
    <HeaderBar />
    <div class="body">
      <SidebarMenu />
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import HeaderBar from './HeaderBar.vue'
import SidebarMenu from './SidebarMenu.vue'
import { useMenuStore } from '../store/menu'

const menuStore = useMenuStore()
onMounted(async () => {
  try {
    await menuStore.fetchMenu()
  } catch (e) {
    // 未登录（后端 302 跟随到 login.html，getMenu 解析失败）→ 跳登录页
    window.location.href = '/login'
  }
})
</script>

<style scoped>
.layout { height: 100vh; display: flex; flex-direction: column; }
.body { flex: 1; display: flex; overflow: hidden; }
.content { flex: 1; overflow: hidden; background: #f0f2f5; }
</style>
