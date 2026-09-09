<template>
  <nav class="sidebar">
    <el-menu :default-active="route.path" router class="menu">
      <template v-for="it in menuStore.standalone" :key="it.key">
        <!-- 在此 standalone 之前插入匹配的 group -->
        <el-sub-menu v-for="g in groupsBefore(it.key)" :key="g.key" :index="g.key">
          <template #title><i :class="g.icon"></i><span>{{ g.title }}</span></template>
          <el-menu-item v-for="sub in g.items" :key="sub.key" :index="sub.url">
            {{ sub.title }}
          </el-menu-item>
        </el-sub-menu>
        <!-- standalone 本身 -->
        <el-menu-item :index="it.url">
          <i :class="it.icon"></i><span>{{ it.title }}</span>
        </el-menu-item>
      </template>
      <!-- before 未命中任何 standalone 的 group，追加到末尾 -->
      <el-sub-menu v-for="g in trailingGroups" :key="g.key" :index="g.key">
        <template #title><i :class="g.icon"></i><span>{{ g.title }}</span></template>
        <el-menu-item v-for="sub in g.items" :key="sub.key" :index="sub.url">
          {{ sub.title }}
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMenuStore } from '../store/menu'

const route = useRoute()
const menuStore = useMenuStore()

const standKeys = computed(() => menuStore.standalone.map(s => s.key))

function groupsBefore(key) {
  return menuStore.groups.filter(g => g.before === key)
}

const trailingGroups = computed(() =>
  menuStore.groups.filter(g => !standKeys.value.includes(g.before))
)
</script>

<style scoped>
.sidebar {
  width: 220px;
  height: 100%;
  background: #fff;
  border-right: 1px solid #e8ecf1;
  overflow-y: auto;
  flex-shrink: 0;
}

/* 自定义滚动条 */
.sidebar::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.menu {
  border-right: none;
}

/* 独立菜单项 */
.menu :deep(.el-menu-item) {
  color: #475569 !important;
  height: 42px;
  line-height: 42px;
  margin: 5px 8px;
  border-radius: 8px;
  font-size: 13px;
  transition: all .2s;
}

.menu :deep(.el-menu-item:hover) {
  background: #f1f5f9 !important;
  color: #1e293b !important;
}

.menu :deep(.el-menu-item.is-active) {
  background: #eef2ff !important;
  color: #4f46e5 !important;
  font-weight: 600;
}

.menu :deep(.el-menu-item i) {
  color: #94a3b8 !important;
  font-size: 14px;
  width: 20px;
  margin-right: 8px;
  transition: color .2s;
}

.menu :deep(.el-menu-item:hover i) {
  color: #475569 !important;
}

.menu :deep(.el-menu-item.is-active i) {
  color: #4f46e5 !important;
}

/* 分组标题 */
.menu :deep(.el-sub-menu__title) {
  color: #64748b !important;
  height: 42px;
  line-height: 42px;
  margin: 5px 8px;
  border-radius: 8px;
  font-size: 13px;
  transition: all .2s;
}

.menu :deep(.el-sub-menu__title:hover) {
  background: #f1f5f9 !important;
  color: #1e293b !important;
}

.menu :deep(.el-sub-menu__title i) {
  color: #94a3b8 !important;
  font-size: 14px;
  width: 20px;
  margin-right: 8px;
}

.menu :deep(.el-sub-menu__title:hover i) {
  color: #475569 !important;
}

.menu :deep(.el-sub-menu__icon-arrow) {
  color: #94a3b8 !important;
}

/* 分组子项 */
.menu :deep(.el-sub-menu .el-menu-item) {
  min-width: auto;
  padding-left: 52px !important;
  height: 36px;
  line-height: 36px;
  font-size: 12px;
  color: #64748b !important;
  margin: 1px 8px 1px 16px;
  border-radius: 6px;
}

.menu :deep(.el-sub-menu .el-menu-item:hover) {
  color: #1e293b !important;
  background: #f8fafc !important;
}

.menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background: #eef2ff !important;
  color: #4f46e5 !important;
  font-weight: 600;
}

/* 子菜单背景 */
.menu :deep(.el-sub-menu .el-menu) {
  background: transparent !important;
}
</style>
