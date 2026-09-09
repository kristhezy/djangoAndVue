<template>
  <header class="header">
    <span class="logo">Krist's Test Platform</span>
    <el-popover placement="bottom" :width="520" trigger="click">
      <template #reference>
        <el-button class="tc-btn" text>测试企业信息</el-button>
      </template>
      <div class="tc-title">常用测试企业信息</div>
      <table class="tc-table">
        <thead><tr><th>Env</th><th>Ver.</th><th>compName</th><th>compID（点击复制）</th></tr></thead>
        <tbody>
          <tr><td rowspan="4">PROD</td><td rowspan="2">SK</td><td>招商版小程序测试企业1</td><td @click="copyId('1021060956165488640')">1021060956165488640</td></tr>
          <tr><td>深圳灰度测试企业5</td><td @click="copyId('1012037449188364288')">1012037449188364288</td></tr>
          <tr><td>R3</td><td>加推测试</td><td @click="copyId('839508475783573504')">839508475783573504</td></tr>
          <tr><td>BS</td><td>仙桃市公路管理局</td><td @click="copyId('871052960422051840')">871052960422051840</td></tr>
          <tr><td rowspan="6">TEST</td><td rowspan="2">SK</td><td>招商版测试企业7</td><td @click="copyId('1017368198385172480')">1017368198385172480</td></tr>
          <tr><td>招商版小程序测试企业8</td><td @click="copyId('1035144123776442368')">1035144123776442368</td></tr>
          <tr><td>R3</td><td>云盘版转介绍3</td><td @click="copyId('846400679986987008')">846400679986987008</td></tr>
          <tr><td>BS</td><td>深圳市兴光电子有限公司</td><td @click="copyId('874593368431542272')">874593368431542272</td></tr>
          <tr><td rowspan="2">JZ</td><td>红蚂蚁家装</td><td @click="copyId('1181172541784809472')">1181172541784809472</td></tr>
          <tr><td>点石家装</td><td @click="copyId('1185152155297222656')">1185152155297222656</td></tr>
        </tbody>
      </table>
    </el-popover>
    <span class="spacer"></span>
    <el-dropdown trigger="click" @command="handleCommand">
      <span class="user-dropdown">
        {{ displayName }}
        <el-icon class="arrow"><ArrowDown /></el-icon>
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

const menuStore = useMenuStore()

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
    }).catch(() => {})
  }
}
</script>

<style scoped>
.header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #eee;
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
  color: #555;
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.user-dropdown:hover {
  color: #4f46e5;
}

.arrow {
  font-size: 12px;
}

.tc-btn {
  font-size: 13px;
  color: #64748b;
}

.tc-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 10px;
  color: #1e293b;
}

.tc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.tc-table th,
.tc-table td {
  border: 1px solid #e2e8f0;
  padding: 5px 8px;
  text-align: left;
}

.tc-table th {
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
}

.tc-table td:nth-child(4) {
  font-family: monospace;
  font-size: 11px;
  cursor: pointer;
}

.tc-table td:nth-child(4):hover {
  color: #4f46e5;
}
</style>
