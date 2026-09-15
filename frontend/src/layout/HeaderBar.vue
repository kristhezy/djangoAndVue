<template>
  <header class="header">
    <span class="logo">Krist's Test Platform</span>
    <el-popover placement="bottom" :width="520" trigger="click">
      <template #reference>
        <el-button class="tc-btn" text>测试企业信息</el-button>
      </template>
      <div class="tc-title">常用测试企业信息</div>
      <table class="tc-table">
        <thead>
          <tr>
            <th>Env</th>
            <th>Ver.</th>
            <th>compName</th>
            <th>compID（点击复制）</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td rowspan="4">PROD</td>
            <td rowspan="2">SK</td>
            <td>招商版小程序测试企业1</td>
            <td class="tc-cid" @click="copyId('1021060956165488640')">1021060956165488640</td>
          </tr>
          <tr>
            <td>深圳灰度测试企业5</td>
            <td class="tc-cid" @click="copyId('1012037449188364288')">1012037449188364288</td>
          </tr>
          <tr>
            <td>R3</td>
            <td>加推测试</td>
            <td class="tc-cid" @click="copyId('839508475783573504')">839508475783573504</td>
          </tr>
          <tr>
            <td>BS</td>
            <td>仙桃市公路管理局</td>
            <td class="tc-cid" @click="copyId('871052960422051840')">871052960422051840</td>
          </tr>
          <tr>
            <td rowspan="6">TEST</td>
            <td rowspan="2">SK</td>
            <td>招商版测试企业7</td>
            <td class="tc-cid" @click="copyId('1017368198385172480')">1017368198385172480</td>
          </tr>
          <tr>
            <td>招商版小程序测试企业8</td>
            <td class="tc-cid" @click="copyId('1035144123776442368')">1035144123776442368</td>
          </tr>
          <tr>
            <td>R3</td>
            <td>云盘版转介绍3</td>
            <td class="tc-cid" @click="copyId('846400679986987008')">846400679986987008</td>
          </tr>
          <tr>
            <td>BS</td>
            <td>深圳市兴光电子有限公司</td>
            <td class="tc-cid" @click="copyId('874593368431542272')">874593368431542272</td>
          </tr>
          <tr>
            <td rowspan="2">JZ</td>
            <td>红蚂蚁家装</td>
            <td class="tc-cid" @click="copyId('1181172541784809472')">1181172541784809472</td>
          </tr>
          <tr>
            <td>点石家装</td>
            <td class="tc-cid" @click="copyId('1185152155297222656')">1185152155297222656</td>
          </tr>
        </tbody>
      </table>
    </el-popover>
    <span class="spacer"></span>
    <div class="theme-group">
      <el-popover placement="bottom-end" :width="140" trigger="click">
        <template #reference>
          <el-button class="theme-btn" text title="主题">
            <i class="fa-solid fa-swatchbook"></i>
          </el-button>
        </template>
        <div class="picker-title">选择主题</div>
        <div class="skin-list">
          <div v-for="s in SKINS" :key="s.key" :class="['skin-item', { active: skin === s.key }]"
            @click="setSkin(s.key)">{{
              s.label }}</div>
        </div>
      </el-popover>
      <el-popover placement="bottom-end" :width="140" trigger="click">
        <template #reference>
          <el-button class="theme-btn" text title="主题色">
            <i class="fa-solid fa-palette"></i>
          </el-button>
        </template>
        <div class="picker-title">选择主题色</div>
        <div class="color-picker">
          <span v-for="c in colors" :key="c.key" :class="['color-dot', { active: themeColor === c.key }]"
            :style="{ background: c.light }" :title="c.label" @click="setColor(c.key)"></span>
        </div>
      </el-popover>
    </div>
    <el-dropdown trigger="click" @command="handleCommand">
      <span class="user-dropdown">
        {{ displayName }}
        <el-icon class="arrow">
          <ArrowDown />
        </el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="logout">退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMenuStore } from '../store/menu'
import { useTheme, SKINS } from '../composables/useTheme'

const menuStore = useMenuStore()
const { skin, setSkin, themeColor, setColor } = useTheme()

const colors = [
  { key: 'indigo', label: '靛蓝', light: '#6366f1' },
  { key: 'blue', label: '蓝色', light: '#3b82f6' },
  { key: 'cyan', label: '青色', light: '#06b6d4' },
  { key: 'emerald', label: '翠绿', light: '#10b981' },
  { key: 'amber', label: '琥珀', light: '#f59e0b' },
  { key: 'orange', label: '橙色', light: '#f97316' },
  { key: 'red', label: '红色', light: '#ef4444' },
  { key: 'rose', label: '玫瑰', light: '#f43f5e' },
  { key: 'purple', label: '紫色', light: '#8b5cf6' },
]

const displayName = computed(() =>
  menuStore.user.rn || menuStore.user.uname || ''
)

function copyId(id) {
  navigator.clipboard.writeText(id).then(() => {
    ElMessage.success('已复制: ' + id)
  })
}

function handleCommand(cmd) {
  if (cmd === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => {
      window.location.href = '/logout'
    }).catch(() => { })
  }
}
</script>

<style scoped>
.header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  gap: 12px;
}

.logo {
  font-weight: 700;
  font-size: 20px;
}

.spacer {
  flex: 1;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.user-dropdown:hover {
  color: var(--color-primary);
}

.arrow {
  font-size: 12px;
}

.tc-btn {
  font-size: 13px;
  color: var(--text-muted);
}

.theme-group {
  display: flex;
  align-items: center;
  gap: 0;
}

.theme-group :deep(.el-button) {
  margin-left: 0px;
}

.theme-btn {
  font-size: 16px;
  color: var(--text-muted);
  padding: 4px 6px !important;
}

.theme-btn:hover {
  color: var(--color-primary);
}

.picker-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.skin-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.skin-item {
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: background .15s, color .15s;
}

.skin-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.skin-item.active {
  background: var(--bg-active);
  color: var(--color-primary);
  font-weight: 600;
}

.color-picker {
  display: grid;
  grid-template-columns: repeat(3, 28px);
  gap: 10px;
  justify-content: center;
  padding: 4px 0;
}

.color-dot {
  display: block;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  border: 3px solid transparent;
  transition: border-color .2s, transform .15s;
}

.color-dot:hover {
  transform: scale(1.15);
}

.color-dot.active {
  border-color: var(--text-primary);
}

.tc-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.tc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.tc-table th,
.tc-table td {
  border: 1px solid var(--border-light);
  padding: 5px 8px;
  text-align: left;
}

.tc-table th {
  background: var(--bg-subtle);
  color: var(--text-muted);
  font-weight: 600;
}

.tc-cid {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 13px;
  cursor: pointer;
}

.tc-cid:hover {
  color: var(--color-primary);
}
</style>
