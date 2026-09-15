<template>
  <nav class="sidebar">
    <el-menu :default-active="route.path" router class="menu">
      <template v-for="it in menuStore.standalone" :key="it.key">
        <!-- 在此 standalone 之前插入匹配的 group -->
        <el-sub-menu v-for="g in groupsBefore(it.key)" :key="g.key" :index="g.key">
          <template #title><i :class="g.icon"></i><span>{{ g.title }}</span></template>
          <el-menu-item v-for="sub in g.items" :key="sub.key" :index="sub.url">
            <i :class="sub.icon" v-if="sub.icon"></i><span>{{ sub.title }}</span>
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
          <i :class="sub.icon" v-if="sub.icon"></i><span>{{ sub.title }}</span>
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
  background: var(--bg-card);
  border-right: 1px solid var(--border-sidebar);
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
  background: var(--scrollbar-thumb);
  border-radius: 4px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover);
}

.menu {
  border-right: none;
  background: var(--bg-card) !important;
}

/* 独立菜单项 */
.menu :deep(.el-menu-item) {
  color: var(--text-secondary) !important;
  height: 42px;
  line-height: 42px;
  margin: 5px 8px;
  border-radius: 8px;
  font-size: 13px;
  transition: all .2s;
}

.menu :deep(.el-menu-item:hover) {
  background: var(--bg-hover) !important;
  color: var(--text-primary) !important;
}

.menu :deep(.el-menu-item.is-active) {
  background: var(--bg-active) !important;
  color: var(--color-primary) !important;
  font-weight: 600;
}

.menu :deep(.el-menu-item i) {
  color: var(--text-placeholder) !important;
  font-size: 14px;
  width: 20px;
  margin-right: 8px;
  transition: color .2s;
}

.menu :deep(.el-menu-item:hover i) {
  color: var(--text-secondary) !important;
}

.menu :deep(.el-menu-item.is-active i) {
  color: var(--color-primary) !important;
}

/* 分组标题 */
.menu :deep(.el-sub-menu__title) {
  color: var(--text-muted) !important;
  height: 42px;
  line-height: 42px;
  margin: 5px 8px;
  border-radius: 8px;
  font-size: 13px;
  transition: all .2s;
}

.menu :deep(.el-sub-menu__title:hover) {
  background: var(--bg-hover) !important;
  color: var(--text-primary) !important;
}

.menu :deep(.el-sub-menu__title i) {
  color: var(--text-placeholder) !important;
  font-size: 14px;
  width: 20px;
  margin-right: 8px;
}

.menu :deep(.el-sub-menu__title:hover i) {
  color: var(--text-secondary) !important;
}

.menu :deep(.el-sub-menu__icon-arrow) {
  color: var(--text-placeholder) !important;
}

/* 分组子项 */
.menu :deep(.el-sub-menu .el-menu-item) {
  min-width: auto;
  padding-left: 40px !important;
  height: 36px;
  line-height: 36px;
  font-size: 12px;
  color: var(--text-muted) !important;
  margin: 1px 8px 1px 8px;
  border-radius: 6px;
}

.menu :deep(.el-sub-menu .el-menu-item:hover) {
  color: var(--text-primary) !important;
  background: var(--bg-subtle) !important;
}

.menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background: var(--bg-active) !important;
  color: var(--color-primary) !important;
  font-weight: 600;
}

.menu :deep(.el-sub-menu .el-menu-item i) {
  font-size: 12px;
  width: 16px;
  margin-right: 6px;
  color: var(--text-placeholder) !important;
}

.menu :deep(.el-sub-menu .el-menu-item:hover i) {
  color: var(--text-primary) !important;
}

.menu :deep(.el-sub-menu .el-menu-item.is-active i) {
  color: var(--color-primary) !important;
}

/* 子菜单背景 */
.menu :deep(.el-sub-menu .el-menu) {
  background: transparent !important;
}
</style>
