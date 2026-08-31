<template>
  <nav class="sidebar">
    <el-menu :default-active="route.path" router class="menu">
      <el-menu-item v-for="it in menuStore.standalone" :key="it.key" :index="it.url">
        <i :class="it.icon"></i><span>{{ it.title }}</span>
      </el-menu-item>
      <el-sub-menu v-for="g in menuStore.groups" :key="g.key" :index="g.key">
        <template #title><i :class="g.icon"></i><span>{{ g.title }}</span></template>
        <el-menu-item v-for="it in g.items" :key="it.key" :index="it.url">
          {{ it.title }}
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useMenuStore } from '../store/menu'
const route = useRoute()
const menuStore = useMenuStore()
</script>

<style scoped>
.sidebar { width: 220px; height: 100%; background: #fff; border-right: 1px solid #eee;
  overflow-y: auto; }
.menu { border-right: none; }
</style>
