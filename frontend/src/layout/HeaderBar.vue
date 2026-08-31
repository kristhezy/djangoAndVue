<template>
  <header class="header">
    <span class="logo">TS-Django</span>
    <span class="spacer"></span>
    <span class="user">{{ menuStore.user.rn || menuStore.user.uname || '' }}</span>
    <a class="logout" href="/logout">退出</a>
  </header>
</template>

<script setup>
import { useMenuStore } from '../store/menu'
const menuStore = useMenuStore()
</script>

<style scoped>
.header { height: 56px; display: flex; align-items: center; padding: 0 20px;
  background: #fff; border-bottom: 1px solid #eee; gap: 12px; }
.logo { font-weight: 700; font-size: 18px; }
.spacer { flex: 1; }
.user { color: #555; }
.logout { color: #e6a23c; text-decoration: none; }
</style>
